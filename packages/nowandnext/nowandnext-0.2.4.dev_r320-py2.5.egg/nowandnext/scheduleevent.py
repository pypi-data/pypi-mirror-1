import datetime
import time
import logging

log = logging.getLogger( __name__ )

from nowandnext.timezones.utc import utc
from nowandnext.textparser import textparser
from schedulething import schedulething
from schedulegap import schedulegap

class scheduleevent( schedulething ):
    """
    A thing in the schedule that we might need to notify some other service of
    """
    EVENT_TYPE="SHOW"
    
    def __init__( self, eventinstance, default_artist="Unknown Artist", default_website="", default_logo="" ):
        self._eventinstance = eventinstance
        self._default_artist = default_artist
        self._createtime = datetime.datetime.now( utc )
        self._default_website = default_website
        self._default_logo = default_logo
        # log.info("New Event: %s" % eventinstance.getEvent().getTitle() )

    def getStartTime(self):
        return self._eventinstance.getStart()
    
    def getEndTime(self):
        return self._eventinstance.getEnd()

    def getTitle(self):
        return self._eventinstance.getEvent().getTitle()

    def ping(self, simplecast ):
        query = {}
        now = datetime.datetime.now( utc )
        # How long till finish?
        delta_to_end = self.getTimeToEnd( now )
        seconds_to_end = self.timedeltaToSeconds( delta_to_end )

        description = self._eventinstance.getEvent().getDescription()
        tp = textparser()
        descdict = tp.translate( tp.parsetodict( description ) )
        
        query['duration'] = seconds_to_end
        query['title'] = self._eventinstance.getEvent().getTitle()
        query['artist'] = descdict.get( 'artist', self._default_artist )
        query['website'] = descdict.get( 'web', self._default_website )
        query['picture'] = descdict.get( 'picture', self._default_logo )
        query['songtype'] = 'S'

        return simplecast.ping( query )
