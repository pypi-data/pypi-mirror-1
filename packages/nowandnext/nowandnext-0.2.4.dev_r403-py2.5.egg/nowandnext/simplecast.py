import urllib
import logging
import socket
import exceptions

log = logging.getLogger( __name__ )

class simplecast(object):
    """
    Represents a connection to a simplecast server
    """
    def __init__(self, host, port ):
        assert type(host) == str
        assert type(port) == int
        self.host = host
        self.port = port

    def ping( self, query ):
        assert type(query) == dict
        params = urllib.urlencode( query )
        url = "http://%s:%s/?%s" % ( self.host, self.port, params )
        log.info( "Pinging: %s" % url )
        try:
            urlstream = urllib.urlopen( url )
            response = urlstream.read().strip()
            log.info("Got response: %s" % response )
            return response
        except exceptions.IOError, se:
            log.exception(se)
            log.critical("Could not ping URL: %s" % url)
            return None
