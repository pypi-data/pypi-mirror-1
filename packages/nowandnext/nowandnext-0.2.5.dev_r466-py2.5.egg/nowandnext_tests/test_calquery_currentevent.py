import datetime
import unittest

from nowandnext_tests.caltestcase import caltestcase
from nowandnext.timezones.utc import utc
from nowandnext.timezones.uk import uk

class test_calquery_currentevent( caltestcase ):
    
    def dotestCurrentEvent(self, thetime, expectedshow ):
        assert type( thetime ) == datetime.datetime
        assert type( expectedshow ) == str
        
        currentEventInstance = self._cal.getCurrentEventInstance( thetime )
        showtitle = currentEventInstance.getEvent().getTitle()
        assert showtitle == expectedshow, "Expected: %s, got %s" % ( expectedshow, showtitle )
        
    def testHootingYard1(self):
        self.dotestCurrentEvent( datetime.datetime( 2008, 5, 29, 17, 30, 1, 0, utc ), "Hooting Yard" )
        
    def testHootingYard2(self):
        self.dotestCurrentEvent( datetime.datetime( 2008, 5, 29, 17, 59, 59, 0, utc ), "Hooting Yard" )
    
    def testHootingYard3(self):
        self.dotestCurrentEvent( datetime.datetime( 2008, 5, 29, 17, 59, 59, 0, tzinfo=uk ), "Hooting Yard" )
    
    def testDeRidder1(self):
        self.dotestCurrentEvent( datetime.datetime( 2008, 5, 26, 14, 59, 59, 0, utc ), "de Ridder Day" )
        
if __name__ == '__main__':
    unittest.main()
