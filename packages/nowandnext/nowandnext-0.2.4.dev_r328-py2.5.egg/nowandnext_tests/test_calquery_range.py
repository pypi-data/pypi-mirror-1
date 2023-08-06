import datetime
import unittest

from nowandnext_tests.caltestcase import caltestcase
from nowandnext.timezones.utc import utc
from nowandnext.timezones.uk import uk

class test_calquery_currentevent( caltestcase ):
    
    def dotestCurrentEvents(self, starttime, endtime, expectedshows ):
        assert type( starttime ) == datetime.datetime
        assert type( endtime ) == datetime.datetime
        
        assert type( expectedshows ) == list
        for expected in expectedshows:
            assert type(expected) == str
        
        currentEventInstances = self._cal.getEventInstances( starttime, endtime )
        currentEventTitles = [ a.getEvent().getTitle() for a in currentEventInstances ]
        
        assert len( expectedshows ) == len( currentEventTitles ), "Got %i events, expected %i events" % ( len( currentEventTitles ), len( expectedshows ) )
        
        for ( expectedshow, gotshow ) in zip( expectedshows, currentEventTitles ):
            assert expectedshow == gotshow, "Expected: %s, got %s" % ( expectedshow, gotshow )
        
    def testSunday(self):
        
        startTime = datetime.datetime( 2008, 5, 25, 10, 30, 1, 0, utc )
        endTime = datetime.datetime( 2008, 5, 25, 21, 15, 1, 0, utc )
        
        expectedevents = [ "Middle East Panorama", "Bonanza", "Calling All Pensioners", "The Rocket 88 Rock N Roll And Doo-Wop Show",
                           "Active Cancellation", "The first annual Alejandro Finisterre table-football tournament", "Audition",
                           "Six Pillars To Persia (Repeat)", "The Organ", "Framework" ]
        
        self.dotestCurrentEvents( startTime, endTime, expectedevents )
        
    def testSaturday(self):
        
        startTime = datetime.datetime( 2008, 5, 31, 13, 35, 1, 0, utc )
        endTime = datetime.datetime( 2008, 5, 31, 17, 35, 1, 0, utc )
        
        expectedevents = [ "Max Tundra's Rotogravure", "The Yummy Mummy School Run Show (repeat)", "OST", "Fillerdelphia",]
        
        self.dotestCurrentEvents( startTime, endTime, expectedevents )
        
if __name__ == '__main__':
    unittest.main()
