import os
import optparse
import ConfigParser

from nowandnext.utils.detectos import osinfo

class cmdline( object ):
    """
    Base class for command line tools.
    """
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