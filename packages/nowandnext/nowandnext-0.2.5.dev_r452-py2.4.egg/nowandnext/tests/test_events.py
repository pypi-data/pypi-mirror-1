import unittest
import datetime
import pprint

from nowandnext.tests.test_basic import test_basic
from nowandnext.utils.cmdline import cmdline
from nowandnext.calendar.calQuery import CalQuery, CalendarException, NoCalendarEntry

class test_events( test_basic, unittest.TestCase ):
    
    def testInstancesOneDayFetch(self):
        now = datetime.datetime.now()
        sometimeinthefuture = now + self.ONE_DAY
        event_instances_a = self.cal.getEventInstances( now , sometimeinthefuture )
        event_instances_b = self.cal.getEventInstances( now , sometimeinthefuture )
        
        assert len( event_instances_a ) == len( event_instances_b )
        
        for (a,b) in zip( event_instances_a, event_instances_b ):
            assert a == b
            assert hash(a) == hash(b)
            assert repr(a) == repr(b)
        
        assert set( event_instances_a ) == set( event_instances_b )
        
    def testInstancesSubsets(self):
        now = datetime.datetime.now()
        
        ta = now - self.ONE_DAY * 4
        tb = now - self.ONE_DAY * 3
        tc = now - self.ONE_DAY * 2
        td = now - self.ONE_DAY * 1
        
        event_instances_a = self.cal.getEventInstances( tb , tc )
        event_instances_b = self.cal.getEventInstances( ta , td )
        
        assert set( event_instances_a ).issubset( set( event_instances_b ) )
        
        
    def testInstancesSubsetEventInstances(self):
        now = datetime.datetime( 2009, 2, 16, 0, 0 )
        sometimeinthefuture = now + self.ONE_DAY
        sometimefurtherinthefuture = sometimeinthefuture + self.ONE_DAY
        
        event_instances_small = set( self.cal.getEventInstances( now , sometimeinthefuture ) )
        event_instances_big = set( self.cal.getEventInstances( now , sometimefurtherinthefuture ) )
        
        msg = ", ".join( [str(a) for a in event_instances_small - event_instances_big ] )
        
        assert event_instances_small.issubset( event_instances_big ), "Events missing from bigger list: %s" % msg
            
    