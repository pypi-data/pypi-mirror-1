import logging
import os

from logging.handlers import SysLogHandler, NTEventLogHandler

log = logging.getLogger( __name__ )

class detectos( object ):
    
    def get_home_dir(self):
        NotImplemented
        
    def get_config_dir(self, appname ):
        NotImplemented
        
    def get_logger(self, appname ):
        NotImplemented
        
class dectedWindows( detectos ):
    ostype = "Windows"
    
    @classmethod
    def valid_instance(cls):
        try:
            osinfo = os.uname()
            return False
        except AttributeError, ae:
            return True
    
    def get_home_dir(self):
        return os.environ.get("USERPROFILE")

    def get_config_dir( self, appname ):
        return os.path.join( self.get_home_dir(), "Application Data", appname )
    
    def get_logger( self, appname ):
        return NTEventLogHandler( appname )

class detectedUNIX( detectos ):
    ostype = "UNIX"
    
    @classmethod
    def valid_instance(cls):
        try:
            osinfo = os.uname()
            return True
        except AttributeError, ae:
            return False
    
    def get_home_dir(self):
        return os.environ.get("HOME")
        
    def get_config_dir( self, appname ):
        return os.path.join( self.get_home_dir() , ".%s" % appname.lower() )
    
    def get_logger( self, appname ):
        return SysLogHandler()

for osc in [ dectedWindows, detectedUNIX ]:
    if osc.valid_instance():
        osinfo = osc()

if __name__ == "__main__":
    print "Repr: %s" % repr( osinfo )
    print "Home: %s" %  osinfo.get_home_dir()
    print "Config: %s" %   osinfo.get_config_dir("TestApp")
    print "Logger: %s" % osinfo.get_logger( "TestApp" )
        