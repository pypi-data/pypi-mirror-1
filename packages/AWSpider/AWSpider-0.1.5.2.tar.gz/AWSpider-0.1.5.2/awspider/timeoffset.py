from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.conch.telnet import Telnet
from twisted.internet.defer import Deferred

import datetime
import time
import random

import logging
logger = logging.getLogger("main")

import pytz

timeservers=["nist1.uccaribe.edu", "nist1-ny.WiTime.net", "time-a.nist.gov", "time-b.nist.gov", "nist1-dc.WiTime.net", "nist1.aol-va.symmetricom.com", "nist1.columbiacountyga.gov", "nist.expertsmi.com", "nist.netservicesgroup.com", "time-a.timefreq.bldrdoc.gov", "time-c.timefreq.bldrdoc.gov", "time.nist.gov", "utcnist.colorado.edu", "utcnist2.colorado.edu", "ntp-nist.ldsbc.edu", "time-nw.nist.gov", "nist1.aol-ca.symmetricom.com", "nist1.symmetricom.com", "nist1-sj.WiTime.net", "nist1-la.WiTime.net"]
random.shuffle(timeservers)

class SimpleTelnet(Telnet):
    
    def __init__( self, *args, **kwargs ):
        self.deferred = Deferred()
        self.data = []
        Telnet.__init__(self, *args, **kwargs )
        
    def dataReceived(self, data):
        self.data.append( data )
    
    def connectionLost( self, reason ):
        self.deferred.callback( "".join(self.data) )

def getTimeOffset():
    
    client = ClientCreator(reactor, SimpleTelnet)
    server = timeservers.pop()
    logger.debug( "Requesting time from %s." % server )
    d = client.connectTCP(server, 13, timeout=5)
    d.addCallback( _getTimeOffsetCallback, server )
    d.addErrback( _getTimeOffsetErrback, 0 )
    return d

def _getTimeOffsetErrback( error, count ):
    if count < 5:
        client = ClientCreator(reactor, SimpleTelnet)
        server = timeservers.pop()
        logger.debug( "Attempt %s failed, requesting time from %s." % (count + 1, server) )
        d = client.connectTCP(server, 13, timeout=5)
        d.addCallback( _getTimeOffsetCallback, server )
        d.addErrback( _getTimeOffsetErrback, count + 1 ) 
        return d   
    else:
        logger.debug( "Could not fetch time after %s attempts." % count )
        return error
        
def _getTimeOffsetCallback( simple_telnet, server ):
    logger.debug( "Connected to time server %s." % server )
    simple_telnet.deferred.addCallback( _getTimeOffsetCallback2, server )
    return simple_telnet.deferred
    
def _getTimeOffsetCallback2( data, server ):
    
    logger.debug( "Got time from %s." % server )

    t = datetime.datetime( 
        2000 + int(data[7:9]), 
        int(data[10:12]), 
        int(data[13:15]),
        int(data[16:18]),
        int(data[19:21]),
        int(data[22:23]),
        tzinfo=pytz.utc )
    
    offset = time.mktime( t.timetuple() ) - time.time()
    return offset

def getTimeOffsetTest():
    d = getTimeOffset()
    d.addCallback(_getTimeOffsetTestCallback)
    
def _getTimeOffsetTestCallback( offset ):
    print offset
    print time.time()
    print time.time() + offset

if __name__ == "__main__":
    import logging.handlers
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s %(pathname)s:%(lineno)d")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    reactor.callWhenRunning( getTimeOffsetTest )     
    reactor.run()