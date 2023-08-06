import unittest
import datetime
import pprint

from nowandnext.utils.cmdline import cmdline
from nowandnext.calendar.calQuery import CalQuery, CalendarException, NoCalendarEntry

class test_basic( cmdline ):
    
    ONE_DAY = datetime.timedelta( days=1 )
    HALF_DAY = datetime.timedelta( days=0.5 )
    TWO_DAYS = ONE_DAY * 2
    CFG = "resonance_pinger.cfg"
    
    def setUp(self):
        configpath = self.getConfigFileLocation( self.CFG )
        config = self.getconfiguration( configpath )
        
        self.calargs=( config.get('pinger','account'),
                       config.get('pinger','password'),
                       config.get('pinger','calendar_name'), )
        
        self.cal = CalQuery( *self.calargs )
        
    def tearDown(self):
        pass
    
    