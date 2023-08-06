import unittest
import ConfigParser

from nowandnext.calQuery import CalQuery
from nowandnext.pinger import pinger

class caltestcase( unittest.TestCase ):
    
    def setUp(self):
        configpath = pinger.getConfigFileLocation( pinger.CONFIG_FILE_NAME )
        self._config = pinger.loadConfig( configpath ) 
        
        self._calargs=( self._config.get('pinger','account'),
                        self._config.get('pinger','password'),
                        self._config.get('pinger','calendar_name'), )
        
        self._cal = foo = CalQuery( *self._calargs )
        
    def tearDown(self):
        del self._cal
        