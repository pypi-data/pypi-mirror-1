import unittest
import datetime
import pprint

from nowandnext.utils.cmdline import cmdline
from nowandnext.calendar.calQuery import CalQuery, CalendarException, NoCalendarEntry

class test_basic( unittest.TestCase, cmdline ):
    
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
            
    
    def testEquivalentEventSearch(self):
        now = datetime.datetime.now()
        earlier = now - self.ONE_DAY
        earlier_still = earlier - self.ONE_DAY
        
        events_a = set( self.cal.getEvents( earlier , now ) )
        events_b = set( self.cal.getEvents( earlier_still , earlier ) )
        events_c = set( self.cal.getEvents( earlier_still, now ) )
        
        events_ab = events_a.union( events_b )
        missing_events = events_c - events_ab
        assert len( missing_events ) == 0, "Events missing: %s" % ", ".join( repr(a) for a in missing_events )

    def testEquivalentEventSearchBigger(self):
        now = datetime.datetime.now()
        earlier = now - self.TWO_DAYS
        earlier_still = earlier - self.TWO_DAYS
        
        events_a = set( self.cal.getEvents( earlier , now ) )
        events_b = set( self.cal.getEvents( earlier_still , earlier ) )
        events_c = set( self.cal.getEvents( earlier_still, now ) )
        
        events_ab = events_a.union( events_b )
        missing_events = events_c - events_ab
        assert len( missing_events ) == 0, "Events missing: %s" % ", ".join( repr(a) for a in missing_events )


    def testEquivalentEventSearchSmaller(self):
        now = datetime.datetime.now()
        earlier = now - self.HALF_DAY
        earlier_still = earlier - self.HALF_DAY
        
        events_a = set( self.cal.getEvents( earlier , now ) )
        events_b = set( self.cal.getEvents( earlier_still , earlier ) )
        events_c = set( self.cal.getEvents( earlier_still, now ) )
        
        events_ab = events_a.union( events_b )        
        missing_events = events_c - events_ab
        
        assert len( missing_events ) == 0, "Events missing: %s" % ", ".join( repr(a) for a in missing_events )

        