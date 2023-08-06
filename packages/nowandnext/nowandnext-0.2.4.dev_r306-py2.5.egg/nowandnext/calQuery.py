import re
import datetime
import urllib
import logging
import datetime

import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar

from nowandnext.gevent import gevent
from nowandnext.gdate import gdatetime
from nowandnext.utc import utc

log = logging.getLogger( __name__ )

class CalendarException( Exception ):
    pass

class CalQuery( object ):
    FEEDPREFIX    = 'http://www.google.com/calendar/feeds/'
    SOURCENAME = "RESONANCE_CALQUERY-0.0.1"
    REMATCHFEEDURL = re.compile( '^' + FEEDPREFIX + '(.*?)/(.*?)/(.*)$' )
    D1H = datetime.timedelta( seconds=60 * 60  )

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

    def getEvents(self, startTime, endTime ):
        query = gdata.calendar.service.CalendarEventQuery( self.username, self.visibility, self.projection )

        assert endTime > startTime, "End time should be after start time."

        query.orderby = "starttime"
        # query.futureevents = "true"
        query.singleevents = "true"

        query.start_max = endTime.isoformat()
        query.start_min = startTime.isoformat()

        log.debug( repr(query) )

        feed = self.calendar_service.CalendarQuery( query )
        for i, an_event in enumerate(feed.entry):
            yield gevent( an_event )

    def getEventInstances(self, startTime, endTime ):
        results = []
        for event in self.getEvents( startTime, endTime ):
            for eventinstance in event.getInstances():
                results.append( eventinstance )
        results.sort()
        return results

