import unittest
import datetime
import pprint
import logging

log = logging.getLogger( __name__ )

from nowandnext.tests.test_basic import test_basic
from nowandnext.calendar.scheduleevent import scheduleevent

class test_schedule_items( test_basic, unittest.TestCase ):
    
    
    def testInstancesOneWeekFetch(self):
        now = datetime.datetime.now()
        evs1 = [ scheduleevent(e) for e in self.cal.getEventInstances( now , now + ( self.ONE_DAY * 3) ) ]
        evs2 = [ scheduleevent(e) for e in self.cal.getEventInstances( now + self.ONE_DAY , now + ( self.ONE_DAY * 2 ) ) ]
        
    def testGetPresenterEmails( self ):
        now = datetime.datetime.now()
        evs1 = [ scheduleevent(e) for e in self.cal.getEventInstances( now  , now + ( self.ONE_DAY * 21) ) ]
        
        email_dict = {}
        
        for ev in evs1:
            ev_description = ev.getDescriptionDict()
            
            try:
                email = ev_description["email"]
                
                if not email in email_dict.keys():
                    email_dict[email] = []
                
                email_dict[email].append( ev )
                
            except KeyError, ke:
                log.warn("No email for %s" % str( ev ) )
                continue
            