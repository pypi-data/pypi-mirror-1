"""
This application translates pings from the itunes NowPlaying plugin and translates them into 
a format that Simplecast can understand. Additionally it ignores events that take place during
a google calendar scheduled event.
"""

"""
Emulate a simplecast webserver
"""

import time
import os
import BaseHTTPServer

from nowandnext.gateway.gatewayhandler import gatewayhandler
from nowandnext.utils.cmdline import cmdline

HOST_NAME = "localhost"
PORT_NUMBER = 8181

class itunes_gateway( cmdline ):
    """
    The main implementation goes here.
    """
    
    
    @classmethod
    def main(self):
        server_class = BaseHTTPServer.HTTPServer
        httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
        print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)  
        

def main(  ):
    itunes_gateway.main( )
    
if __name__ == '__main__':
    main()
    
