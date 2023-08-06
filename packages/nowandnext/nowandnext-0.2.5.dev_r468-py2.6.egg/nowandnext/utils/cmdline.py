import os
import sys
import optparse
import ConfigParser
import logging
import pkg_resources

from nowandnext.utils.detectos import osinfo

log = logging.getLogger( __name__ )

class cmdline( object ):
    """
    Base class for command line tools.
    """
    CONFIG_FILE_NAME = "resonance_pinger.cfg"
    
    def getconfiguration( self, config ):
        if os.path.exists( config ) and os.path.isfile( config ):
                return self.loadConfig( config )
                
                log.warn( "Loaded config from %s" % config )
        else:
            log.warn("Config file %s is missing!" % config )
            
            configdir, configfilename = os.path.split( config )
            
            if not os.path.exists( configdir ):
                os.makedirs( configdir )
                log.warn( "New confiuration directory %s made." % configdir )
            if not os.path.exists( config ):
                default_config = pkg_resources.resource_string(__name__, 'data/resonance_pinger.cfg.example')
                file( config , "w" ).write( default_config )
                log.warn( "Default configuration written to %s, please edit it!" % configdir )
            
            sys.exit("Please configure the application by editing the script at: %s" % config )
    
    @staticmethod
    def getConfigFileLocation( configfilename ):
        configdir = osinfo.get_config_dir( "Pinger" )
        configfilepath = os.path.join( configdir, configfilename )
        return configfilepath
    
    @staticmethod
    def loadConfig( configfilepath ):
        configdir, configfilename = os.path.split( configfilepath )
        assert os.path.exists( configfilepath ) and os.path.isfile( configfilepath )
        config = ConfigParser.SafeConfigParser()
        configfile = file( configfilepath )
        config.readfp( configfile, configfilename )
        return config
    
    @staticmethod
    def copyrightmessage():
        print "This product is released under the GPL"
        print "Documentation is here: http://code.google.com/p/suxtools/wiki/Pinger"
        print "To Exit: CTRL-Break or CTRL-C"
        print "Or just type: easy_install -U nowandnext"
        print "For tech support contact sal@stodge.org"
        print "Or m. 07973 710 574"
        print "(c) 2008 Salim Fadhley"
    
    @classmethod
    def mkParser( cls ):
        parser = optparse.OptionParser()
        defaultconfigfilelocation = cls.getConfigFileLocation( cls.CONFIG_FILE_NAME )
        parser.add_option( "--configfile", dest="configfilepath",
                           help="The location of the configuration file, default is: %s" % defaultconfigfilelocation,
                           default=defaultconfigfilelocation, type="str" )

        parser.add_option( "--quiet", "-q", dest="verbose",
                           help="Make the logging less verbose",
                           default=True, action="store_false" )

        parser.add_option( "--warpfactor", "-w", dest="warpfactor",
                           help="Make time appear to go faster - handy for debugging the script but never for production use.",
                           default=1.0, type="float" )
        
        parser.add_option( "--debugmode", "-d", dest="debugmode",
                           help="Crash out on critical failure.",
                           default=False, action="store_true" )

        return parser