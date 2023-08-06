import re
import datetime
import urllib
import logging
import datetime

import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar

from nowandnext.calendar.gevent import gevent
from nowandnext.calendar.gdate import gdatetime
from nowandnext.timezones.utc import utc

log = logging.getLogger( __name__ )

class CalendarException( Exception ):
    pass

class NoCalendarEntry( CalendarException ):
    """
    Raised when no calendar entry matches the criteria. 
    """

class CalQuery( object ):
    FEEDPREFIX    = 'http://www.google.com/calendar/feeds/'
    SOURCENAME = "RESONANCE_CALQUERY-0.0.2"
    REMATCHFEEDURL = re.compile( '^' + FEEDPREFIX + '(.*?)/(.*?)/(.*)$' )
    
    # One Hour
    D1H = datetime.timedelta( seconds=60 * 60  )
    
    # How much time can we search through at any one go?
    MAX_SAFE_SEARCH_WINDOW = D1H * 12
    
    # How many times should we search backwards from the present date before giving up?
    NUMBER_OF_SEARCH_ITERATIONS = 14

    def __init__(self, username, password, calendarname ):
        self.calendarname = "Resonance Schedule"
        self.calendar_service = gdata.calendar.service.CalendarService()
        self.calendar_service.email = username
        self.calendar_service.password = password
        self.calendar_service.source = self.SOURCENAME
        self.calendar_service.ProgrammaticLogin()
        self.calendar = self.getCalendar( self.calendar_service, calendarname )
        self.username, self.visibility, self.projection = self.parseCalendar( self.calendar )

    @classmethod
    def parseCalendar( cls, cal ):
        caluri = cal.GetAlternateLink().href
        match = cls.REMATCHFEEDURL.match( caluri )
        assert match, "Could not parse %s" % cal
        username    = urllib.unquote(match.group(1))
        visibility  = urllib.unquote(match.group(2))
        projection  = urllib.unquote(match.group(3))

        return username, visibility, projection

    @classmethod
    def getCalendar( cls, calendar_service, calname ):
        feed = calendar_service.GetAllCalendarsFeed()
        for i, a_calendar in enumerate(feed.entry):
            try:
                cal_title = a_calendar.title.text.strip()
            except AttributeError, ae:
                raise CalendarException(ae[0])
            if cal_title == calname.strip():
                return a_calendar
        raise KeyError("Calendar %s does not exist" % calname )

    def getCurrentEventInstance( self, now ):
        """
        Search back in time until we have an event to consider:
        """
        assert isinstance( now, datetime.datetime ), "Got %s, expected %s" % ( repr(now), datetime.datetime )
        
        for count in range(0, self.NUMBER_OF_SEARCH_ITERATIONS ):
            endTime = now - ( count * self.MAX_SAFE_SEARCH_WINDOW )
            startTime = now - ( ( count + 1 ) * self.MAX_SAFE_SEARCH_WINDOW )
            
            eventinstances = [ a for a in self.getEventInstances( startTime, endTime ) ]
            if len(eventinstances) == 0:
                continue
        
            lastEventInstance = eventinstances[-1:][0]
            
            if lastEventInstance.getEnd() < now:                
                # The most recent event has already finished!
                raise NoCalendarEntry("No current event for %s" % now )
            
            return lastEventInstance
            
                 

    def getEvents(self, startTime, endTime ):
        assert endTime > startTime, "End time should be after start time."
        
        query = gdata.calendar.service.CalendarEventQuery( self.username, self.visibility, self.projection )
        
        query.orderby = "starttime"
        query.singleevents = "true"

        query.start_max = endTime.isoformat()
        query.start_min = startTime.isoformat()
        query.max_results = "99999"

        log.debug( repr(query) )

        feed = self.calendar_service.CalendarQuery( query )
        
        for an_event in feed.entry:
            yield gevent( an_event )

    def getEventInstances(self, startTime, endTime ):
        results = []
        for event in self.getEvents( startTime, endTime ):
            for eventinstance in event.getInstances():
                results.append( eventinstance )
        results.sort()
        return results

