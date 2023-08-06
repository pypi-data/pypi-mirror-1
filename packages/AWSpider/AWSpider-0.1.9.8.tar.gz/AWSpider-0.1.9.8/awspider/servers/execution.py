import cPickle
import time
import pprint
from twisted.web.client import _parse
from uuid import uuid5, NAMESPACE_DNS
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet import task
from twisted.internet import reactor
from twisted.web import server
from .base import BaseServer, LOGGER
from ..aws import sdb_now, sdb_now_add
from ..resources import ExecutionResource
from ..networkaddress import getNetworkAddress

PRETTYPRINTER = pprint.PrettyPrinter(indent=4)

class ExecutionServer(BaseServer):
    
    peers = {}
    peer_uuids = []
    reportjobspeedloop = None
    jobsloop = None
    queryloop = None
    coordinateloop = None  
    uuid_limits = {'start':None, 'end':None}
    public_ip = None
    local_ip = None
    network_information = {}
    queued_jobs = {}
    job_queue = []
    job_count = 0
    query_start_time = None
    simultaneous_jobs = 50
    
    def __init__(self,
            aws_access_key_id, 
            aws_secret_access_key, 
            aws_sdb_reservation_domain, 
            aws_s3_http_cache_bucket=None, 
            aws_s3_storage_bucket=None,
            aws_sdb_coordination_domain=None,
            max_simultaneous_requests=150,
            max_requests_per_host_per_second=1,
            max_simultaneous_requests_per_host=5,
            port=5001, 
            log_file='executionserver.log',
            log_directory=None,
            log_level="debug",
            name=None,
            time_offset=None,
            peer_check_interval=60,
            reservation_check_interval=60,
            hammer_prevention=True):
        if name == None:
            name = "AWSpider Execution Server UUID: %s" % self.uuid
        self.network_information["port"] = port
        self.hammer_prevention = hammer_prevention
        self.peer_check_interval = int(peer_check_interval)
        self.reservation_check_interval = int(reservation_check_interval)
        resource = ExecutionResource(self)
        self.site_port = reactor.listenTCP(port, server.Site(resource))
        BaseServer.__init__(
            self,
            aws_access_key_id, 
            aws_secret_access_key, 
            aws_s3_http_cache_bucket=aws_s3_http_cache_bucket, 
            aws_sdb_reservation_domain=aws_sdb_reservation_domain, 
            aws_s3_storage_bucket=aws_s3_storage_bucket,
            aws_sdb_coordination_domain=aws_sdb_coordination_domain,
            max_simultaneous_requests=max_simultaneous_requests,
            max_requests_per_host_per_second=max_requests_per_host_per_second,
            max_simultaneous_requests_per_host=max_simultaneous_requests_per_host,
            log_file=log_file,
            log_directory=log_directory,
            log_level=log_level,
            name=name,
            time_offset=time_offset,
            port=port)

    def start(self):
        reactor.callWhenRunning(self._start)
        return self.start_deferred

    def _start(self):
        deferreds = []
        deferreds.append(self.getNetworkAddress())
        if self.time_offset is None:
            deferreds.append(self.getTimeOffset())
        d = DeferredList(deferreds, consumeErrors=True)
        d.addCallback(self._startCallback)

    def _startCallback(self, data):
        for row in data:
            if row[0] == False:
                d = self.shutdown()
                d.addCallback(self._startHandleError, row[1])
                return d
        d = BaseServer.start(self)   
        d.addCallback(self._startCallback2)

    def _startCallback2(self, data):
        if self.shutdown_trigger_id is not None:
            self.reportjobspeedloop = task.LoopingCall(self.reportJobSpeed)
            self.reportjobspeedloop.start(60)
            self.jobsloop = task.LoopingCall(self.executeJobs)
            self.jobsloop.start(1)
            self.queryloop = task.LoopingCall(self.query)
            self.queryloop.start(self.reservation_check_interval)
            if self.aws_sdb_coordination_domain is not None:
                self.coordinateloop = task.LoopingCall(self.coordinate)
                self.coordinateloop.start(self.peer_check_interval)  
                self.peerCheckRequest()
        
    def shutdown(self):
        LOGGER.critical("Shutting down.")
        self.job_queue = []
        self.queued_jobs = {}
        deferreds = []
        LOGGER.debug("%s stopping on main HTTP interface." % self.name)
        d = self.site_port.stopListening()
        if isinstance(d, Deferred):
            deferreds.append(d)
        if self.reportjobspeedloop is not None:
            LOGGER.debug("Stopping report job speed loop.")
            d = self.reportjobspeedloop.stop()
            if isinstance(d, Deferred):
                deferreds.append(d)            
        if self.jobsloop is not None:
            LOGGER.debug("Stopping jobs loop.")
            d = self.jobsloop.stop()
            if isinstance(d, Deferred):
                deferreds.append(d)           
        if self.queryloop is not None:
            LOGGER.debug("Stopping query loop.")
            d = self.queryloop.stop()
            if isinstance(d, Deferred):
                deferreds.append(d)
        if self.coordinateloop is not None:
            LOGGER.debug("Stopping coordinating loop.")
            d = self.coordinateloop.stop()
            if isinstance(d, Deferred):
                deferreds.append(d)
            LOGGER.debug( "Removing data from SDB coordination domain.")
            d = self.sdb.delete(self.aws_sdb_coordination_domain, self.uuid )
            d.addCallback(self.peerCheckRequest)
            deferreds.append(d)
        if len(deferreds) > 0:
            d = DeferredList(deferreds)
            d.addCallback(self._shutdownCallback)
            return d
        else:
            return self._shutdownCallback(None)
    
    def _shutdownCallback(self, data):
        return BaseServer.shutdown(self)

    def peerCheckRequest(self, data=None):
        LOGGER.debug("Signaling peers.")
        deferreds = []
        for uuid in self.peers:
            if uuid != self.uuid and self.peers[uuid]["active"]:
                LOGGER.debug("Signaling %s to check peers." % self.peers[uuid]["uri"])
                d = self.rq.getPage(self.peers[uuid]["uri"] + "/coordinate", prioritize=True)
                d.addCallback(self._peerCheckRequestCallback, self.peers[uuid]["uri"])
                d.addErrback(self, _peerCheckRequestErrback, self.peers[uuid]["uri"])
                deferreds.append(d)
        if len(deferreds) > 0:
            LOGGER.debug("Combinining shutdown signal deferreds.")
            return DeferredList(deferreds, consumeErrors=True)
        return True
    
    def _peerCheckRequestErrback(self, error, uri):
        LOGGER.debug("Could not get %s/coordinate: %s" % (uri, str(error)))
        
    def _peerCheckRequestCallback(self, data, uri):
        LOGGER.debug("Got %s/coordinate." % uri)

    def getNetworkAddress(self):
        d = getNetworkAddress()
        d.addCallback(self._getNetworkAddressCallback)
        d.addErrback(self._getNetworkAddressErrback)
        return d

    def _getNetworkAddressCallback( self, data  ):   
        if "public_ip" in data:
            self.public_ip = data["public_ip"]
            self.network_information["public_ip"] = self.public_ip
        if "local_ip" in data:
            self.local_ip = data["local_ip"]  
            self.network_information["local_ip"] = self.local_ip

    def _getNetworkAddressErrback(self, error):
        message = "Could not get network address." 
        LOGGER.error(message)
        raise Exception(message)

    def coordinate(self):
        attributes = {"created":sdb_now(offset=self.time_offset)}
        attributes.update(self.network_information)
        d = self.sdb.putAttributes(
            self.aws_sdb_coordination_domain, 
            self.uuid, 
            attributes, 
            replace=attributes.keys())
        d.addCallback(self._coordinateCallback)
        d.addErrback(self._coordinateErrback)
        
    def _coordinateCallback( self, data ):
        sql = "SELECT public_ip, local_ip, port FROM `%s` WHERE created > '%s'" % (
            self.aws_sdb_coordination_domain, 
            sdb_now_add(self.peer_check_interval * -2, 
            offset=self.time_offset))
        LOGGER.debug( "Querying SimpleDB, \"%s\"" % sql )
        d = self.sdb.select(sql)
        d.addCallback(self._coordinateCallback2)
        d.addErrback(self._coordinateErrback)

    def _coordinateCallback2(self, discovered):
        existing_peers = set(self.peers.keys())
        discovered_peers = set(discovered.keys())
        new_peers = discovered_peers - existing_peers
        old_peers = existing_peers - discovered_peers
        for uuid in old_peers:
            LOGGER.debug("Removing peer %s" % uuid)
            if uuid in self.peers:
                del self.peers[uuid]
        deferreds = []
        for uuid in new_peers:
            if uuid == self.uuid:
                self.peers[uuid] = {
                    "uri":"http://127.0.0.1:%s" % self.port,
                    "local_ip":"127.0.0.1",
                    "port":self.port,
                    "active":True
                }
            else:
                deferreds.append(self.verifyPeer(uuid, discovered[uuid]))
        if len(new_peers) > 0:
            if len(deferreds) > 0:
                d = DeferredList(deferreds, consumeErrors=True)
                d.addCallback(self._coordinateCallback3)
            else:
                self._coordinateCallback3(None) #Just found ourself.
        elif len(old_peers) > 0:
            self._coordinateCallback3(None)
        else:
            pass # No old, no new.

    def _coordinateCallback3(self, data):
        LOGGER.debug( "Re-organizing peers." )
        for uuid in self.peers:
            if "local_ip" in self.peers[uuid]:
                self.peers[uuid]["uri"] = "http://%s:%s" % (self.peers[uuid]["local_ip"], self.peers[uuid]["port"] )
                self.peers[uuid]["active"] = True
                self.rq.setHostMaxRequestsPerSecond(self.peers[uuid]["local_ip"], 0)
                self.rq.setHostMaxSimultaneousRequests(self.peers[uuid]["local_ip"], 0)
            elif "public_ip" in self.peers[uuid]:
                self.peers[uuid]["uri"] = "http://%s:%s" % (self.peers[uuid]["public_ip"], self.peers[uuid]["port"] )
                self.peers[uuid]["active"] = True
                self.rq.setHostMaxRequestsPerSecond(self.peers[uuid]["public_ip"], 0)
                self.rq.setHostMaxSimultaneousRequests(self.peers[uuid]["public_ip"], 0)
            else:
                LOGGER.error("Peer %s has no local or public IP. This should not happen." % uuid )
        self.peer_uuids = self.peers.keys()
        self.peer_uuids.sort()
        LOGGER.debug("Peers updated to: %s" % self.peers)
        # Set UUID peer limits by splitting up lexicographical namespace using hex values.
        peer_count = len(self.peers)
        splits = [hex(4096/peer_count * x)[2:] for x in range(1, peer_count)]
        splits = zip([None] + splits, splits + [None])
        splits = [{"start":x[0], "end":x[1]} for x in splits]
        if self.uuid in self.peer_uuids:
            self.uuid_limits = splits[self.peer_uuids.index(self.uuid)]
        else:
            self.uuid_limits = {"start":None, "end":None}
        LOGGER.debug( "Updated UUID limits to: %s" % self.uuid_limits)
        
    def _coordinateErrback(self, error):
        LOGGER.error( "Could not query SimpleDB for peers: %s" % str(error) )

    def verifyPeer(self, uuid, peer):
        LOGGER.debug( "Verifying peer %s" % uuid )
        deferreds = []
        if "port" in peer:
            port = int(peer["port"][0])
        else:
            port = self.port
        if uuid not in self.peers:
            self.peers[uuid] = {}
        self.peers[uuid]["active"] = False
        self.peers[uuid]["port"] = port
        if "local_ip" in peer:
            local_ip = peer["local_ip"][0]
            local_url = "http://%s:%s/server" % (local_ip, port)
            d = self.rq.getPage(local_url, timeout=5, prioritize=True)
            d.addCallback(self._verifyPeerLocalIPCallback, uuid, local_ip, port)
            deferreds.append( d )
        if "public_ip" in peer:
            public_ip = peer["public_ip"][0]
            public_url = "http://%s:%s/server" % (public_ip, port)
            d = self.rq.getPage(public_url, timeout=5, prioritize=True)
            d.addCallback(self._verifyPeerPublicIPCallback, uuid, public_ip, port)
            deferreds.append(d)
        if len(deferreds) > 0:
            d = DeferredList(deferreds, consumeErrors=True)
            return d
        else:
            return None

    def _verifyPeerLocalIPCallback(self, data, uuid, local_ip, port):
        LOGGER.debug("Verified local IP for %s" % uuid)
        self.peers[uuid]["local_ip"] = local_ip

    def _verifyPeerPublicIPCallback(self, data, uuid, public_ip, port):
        LOGGER.debug("Verified public IP for %s" % uuid)
        self.peers[uuid]["public_ip"] = public_ip

    def getPage(self, *args, **kwargs):
        if not self.hammer_prevention or len(self.peer_uuids) == 0:
            return self.pg.getPage(*args, **kwargs)
        else:
            scheme, host, port, path = _parse(args[0])
            peer_key = int(uuid5(NAMESPACE_DNS, host).int % len(self.peer_uuids))
            peer_uuid = self.peer_uuids[peer_key]
            if peer_uuid == self.uuid or self.peers[peer_uuid]["active"] == False:
                return self.pg.getPage(*args, **kwargs)
            else:
                parameters = {}
                parameters["url"] = args[0]
                if "method" in kwargs:
                    parameters["method"] = kwargs["method"]   
                if "postdata" in kwargs: 
                    parameters["postdata"] = urllib.urlencode(kwargs["postdata"])
                if "headers" in kwargs: 
                    parameters["headers"] = urllib.urlencode(kwargs["headers"])
                if "cookies" in kwargs: 
                    parameters["cookies"] = urllib.urlencode(kwargs["cookies"])         
                if "agent" in kwargs:
                    parameters["agent"] = kwargs["agent"]
                if "timeout" in kwargs:
                    parameters["timeout"] = kwargs["timeout"]
                if "followRedirect" in kwargs:
                    parameters["followRedirect"] = kwargs["followRedirect"]
                if "url_hash" in kwargs: 
                    parameters["url_hash"] = kwargs["url_hash"]
                if "cache" in kwargs: 
                    parameters["cache"] = kwargs["cache"]
                if "prioritize" in kwargs: 
                    parameters["prioritize"] = kwargs["prioritize"]
                url = "%s/getpage?%s" % (
                    self.peers[peer_uuid]["uri"], 
                    urllib.urlencode(parameters))
                LOGGER.debug("Re-routing request for %s to %s" % (args[0], url))
                d = self.rq.getPage(url, prioritize=True)
                d.addErrback(self._getPageErrback, args, kwargs) 
                return d

    def _getPageErrback( self, error, args, kwargs):
        LOGGER.error(args[0] + ":" + str(error))
        return self.pg.getPage(*args, **kwargs)

    def queryByUUID(self, uuid):
        sql = "SELECT * FROM `%s` WHERE itemName() = '%s'" % (self.aws_sdb_reservation_domain, uuid)
        LOGGER.debug("Querying SimpleDB, \"%s\"" % sql)
        d = self.sdb.select(sql)
        d.addCallback(self._queryCallback2)
        d.addErrback(self._queryErrback)        
        return d

    def query(self, data=None):
        if self.uuid_limits["start"] is None and self.uuid_limits["end"] is not None:
            uuid_limit_clause = "AND itemName() < '%s'" % self.uuid_limits["end"]
        elif self.uuid_limits["start"] is not None and self.uuid_limits["end"] is None:
            uuid_limit_clause = "AND itemName() > '%s'" % self.uuid_limits["start"]
        elif self.uuid_limits["start"] is None and self.uuid_limits["end"] is None:
            uuid_limit_clause = ""
        else:
            uuid_limit_clause = "AND itemName() BETWEEN '%s' AND '%s'" % (self.uuid_limits["start"], self.uuid_limits["end"])
        sql = """SELECT itemName() 
                FROM `%s` 
                WHERE
                reservation_next_request < '%s' %s
                LIMIT 2500""" % (    
                self.aws_sdb_reservation_domain, 
                sdb_now(offset=self.time_offset),
                uuid_limit_clause)
        LOGGER.debug("Querying SimpleDB, \"%s\"" % sql)
        d = self.sdb.select(sql)
        d.addCallback(self._queryCallback)
        d.addErrback(self._queryErrback)

    def _queryErrback(self, error):
        LOGGER.error("Unable to query SimpleDB.\n%s" % error)

    def _queryCallback(self, data):
        deferreds = []
        keys = data.keys()
        if len(keys) > 0:
            i = 0
            while i * 20 < len(keys):
                key_subset = keys[i*20:(i+1)*20]
                i += 1
                sql = """SELECT *
                        FROM `%s` 
                        WHERE
                        itemName() in('%s')
                        """ % (
                        self.aws_sdb_reservation_domain, 
                        "','".join(key_subset))
                LOGGER.debug("Querying SimpleDB, \"%s\"" % sql)
                d = self.sdb.select(sql)
                d.addCallback(self._queryCallback2)
                d.addErrback(self._queryErrback) 
                deferreds.append(d)
            d = DeferredList(deferreds)
            d.addCallback(self._queryCallback3)
            
    def _queryCallback3(self, data):
        self.job_count = 0
        self.query_start_time = time.time()
                            
    def _queryCallback2(self, data):
        # Iterate through the reservation data returned from SimpleDB
        for uuid in data:
            if uuid in self.active_jobs or uuid in self.queued_jobs:
                continue
            kwargs_raw = {}
            reserved_arguments = {}
            # Load attributes into dicts for use by the system or custom functions.
            for key in data[uuid]:
                if key in self.reserved_arguments:
                    reserved_arguments[key] = data[uuid][key][0]
                else:
                    kwargs_raw[key] = data[uuid][key][0]
            # Check to make sure the custom function is present.
            function_name = reserved_arguments["reservation_function_name"]
            if function_name not in self.functions:
                LOGGER.error("Unable to process function %s for UUID: %s" % (function_name, uuid))
                continue
            # Check for the presence of all required system attributes.
            if "reservation_function_name" not in reserved_arguments:
                LOGGER.error("Reservation %s does not have a function name." % uuid)
                self.deleteReservation(uuid)
                continue
            if "reservation_created" not in reserved_arguments:
                LOGGER.error("Reservation %s, %s does not have a created time." % (function_name, uuid))
                self.deleteReservation( uuid, function_name=function_name )
                continue
            if "reservation_next_request" not in reserved_arguments:
                LOGGER.error("Reservation %s, %s does not have a next request time." % (function_name, uuid))
                self.deleteReservation( uuid, function_name=function_name )
                continue                
            if "reservation_error" not in reserved_arguments:
                LOGGER.error("Reservation %s, %s does not have an error flag." % (function_name, uuid))
                self.deleteReservation( uuid, function_name=function_name )
                continue
            # Load custom function.
            if function_name in self.functions:
                exposed_function = self.functions[function_name]
            else:
                LOGGER.error("Could not find function %s." % function_name)
                continue
            # Check for required / optional arguments.
            kwargs = {}
            for key in kwargs_raw:
                if key in exposed_function["required_arguments"]:
                    kwargs[key] = kwargs_raw[key]
                if key in exposed_function["optional_arguments"]:
                    kwargs[key] = kwargs_raw[key]
            has_reqiured_arguments = True
            for key in exposed_function["required_arguments"]:
                if key not in kwargs:
                    has_reqiured_arguments = False
                    LOGGER.error("%s, %s does not have required argument %s." % (function_name, uuid, key))
            if not has_reqiured_arguments:
                continue
            self.queued_jobs[uuid] = True
            self.job_queue.append({
                "exposed_function":exposed_function,
                "kwargs":kwargs,
                "function_name":function_name,
                "uuid":uuid
            })
        self.executeJobs()
    
    def reportJobSpeed(self):
        if self.query_start_time is not None and self.job_count > 0:
            seconds_per_job = (time.time() - self.query_start_time) / self.job_count
            LOGGER.critical("Average execution time: %s, %s active." % (seconds_per_job, len(self.active_jobs)))
        else:
            LOGGER.critical("No average speed to report yet.")
            
    def executeJobs(self, data=None):
        while len(self.job_queue) > 0 and len(self.active_jobs) < self.simultaneous_jobs:
            job = self.job_queue.pop(0)
            exposed_function = job["exposed_function"]
            kwargs = job["kwargs"]
            function_name = job["function_name"]
            uuid = job["uuid"]
            del self.queued_jobs[uuid]
            # Call the function.
            LOGGER.debug("Calling %s with args %s" % (function_name, kwargs))
            # Schedule the next request.
            reservation_next_request_parameters = {
                "reservation_next_request":sdb_now_add(
                    exposed_function["interval"], 
                    offset=self.time_offset)}
            d = self.sdb.putAttributes(
                self.aws_sdb_reservation_domain, 
                uuid, 
                reservation_next_request_parameters, 
                replace=["reservation_next_request"])
            d.addCallback(self._setNextRequestCallback, function_name, uuid)
            d.addErrback(self._setNextRequestErrback, function_name, uuid)
            d = self.callExposedFunction(
                exposed_function["function"], 
                kwargs, 
                function_name, 
                uuid)
            d.addCallback(self._jobCountCallback)
            d.addErrback(self._jobCountErrback)
            
    def _jobCountCallback(self, data):
        self.job_count += 1
        
    def _jobCountErrback(self, error):
        self.job_count += 1
        
    def _setNextRequestCallback(self, data, function_name, uuid):
        LOGGER.debug("Set next request for %s, %s on on SimpleDB." % (function_name, uuid))

    def _setNextRequestErrback(self, error, function_name, uuid):
        LOGGER.error("Unable to set next request for %s, %s on SimpleDB.\n%s" % (function_name, uuid, error.value))

