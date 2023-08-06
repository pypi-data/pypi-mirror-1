import logging
import datetime

from nowandnext.calendar.schedulething import schedulething
from nowandnext.timezones.utc import utc

log = logging.getLogger( __name__ )

class schedulegap( schedulething ):
    """
    Represents a gap in the schedule.
    """
    EVENT_TYPE="GAP"
    
    def __init__( self, startTime, endTime, default_title="", default_artist="", default_website="", default_description="", default_logo="" ):
        assert isinstance(startTime, datetime.datetime,  )
        assert isinstance(endTime, datetime.datetime,  )
        assert type(default_title) == str
        assert type(default_artist) == str
        assert type(default_website) == str
        assert type(default_description) == str
        assert type(default_logo) == str
        
        #log.info( "New schedulegap: %s to %s" % ( startTime, endTime ) )
        self._startTime = startTime
        self._endTime = endTime
        self._title = default_title
        self._artist = default_artist
        self._website = default_website
        self._description = default_description
        self._logo = default_logo
        
    def getStartTime(self):
        return self._startTime
    
    def getEndTime(self):
        return self._endTime
    
    def getTitle(self):
        return self._title
    
    def ping(self, simplecast ):
        query = {}
        now = datetime.datetime.now( utc )
        # How long till finish?
        delta_to_end = self.getTimeToEnd( now )
        seconds_to_end = self.timedeltaToSeconds( delta_to_end )
        
        query['duration'] = seconds_to_end
        query['title'] = self._title
        query['artist'] = self._artist
        query['website'] = self._website
        query['picture'] = self._logo
        
        query['songtype'] = 'S'

        return simplecast.ping( query )
        
    
