import datetime
import time
import logging

log = logging.getLogger( __name__ )

from nowandnext.utc import utc
from nowandnext.textparser import textparser

class scheduleevent( object ):
    """
    A thing in the schedule that we might need to notify some other service of
    """
    SECONDS_IN_A_DAY = 60 * 60 * 24

    def __init__( self, eventinstance, default_artist="Unknown Artist" ):
        self._eventinstance = eventinstance
        self._default_artist = default_artist
        self._createtime = datetime.datetime.now( utc )
        log.info("New Event: %s" % eventinstance.getEvent().getTitle() )

    @classmethod
    def sleepdelta( cls, td, warpfactor=1.0 ):
        assert isinstance( td, datetime.timedelta )
        seconds = cls.timedeltaToSeconds( td ) / float( warpfactor )
        assert seconds >= 0.0, "Cannot sleep a negative amount of time!"
        log.info("Sleeping for %.2f seconds, warp-factor = %.1f" % ( seconds, warpfactor ) )
        time.sleep( seconds )

    @classmethod
    def timedeltaToSeconds( cls, td ):
        dayseconds = td.days * cls.SECONDS_IN_A_DAY
        microsecondseconds = td.microseconds / 1000000.0
        return dayseconds + td.seconds + microsecondseconds

    def sleep_until_event_starts(self, warpfactor=1.0, bias=0):
        now = datetime.datetime.now( utc )
        bias = datetime.timedelta( seconds = bias )
        delta_to_event_start = self._eventinstance.timeToStart( now ) + bias

        if delta_to_event_start <= datetime.timedelta():
            log.info( "Event '%s' has already started!" % self._eventinstance.getEvent().getTitle() )
        else:
            log.info( "Next event: %s starts in delta:%s, local time:%s." % ( self._eventinstance.getEvent().getTitle(),
                                                                      delta_to_event_start,
                                                                      self._eventinstance.getStart().strftime("%Y/%m/%d %H:%M") ) )
            self.sleepdelta( delta_to_event_start, warpfactor=warpfactor )

    def run(self, simplecast, warpfactor = 1.0 ):
        log.debug("Next event: %s @ %s GMT" % ( self._eventinstance.getEvent().getTitle(), self._eventinstance.getStart() ) )
        self.sleep_until_event_starts( warpfactor=warpfactor )
        return self.ping( simplecast )


    def ping(self, simplecast ):
        query = {}
        now = datetime.datetime.now( utc )
        # How long till finish?
        delta_to_end = self._eventinstance.timeToEnd( now )
        seconds_to_end = self.timedeltaToSeconds( delta_to_end )

        description = self._eventinstance.getEvent().getDescription()
        tp = textparser()
        descdict = tp.translate( tp.parsetodict( description ) )

        query['duration']=seconds_to_end
        query['title']=self._eventinstance.getEvent().getTitle()
        query['artist']=self._default_artist
        query['songtype']='S'

        return simplecast.ping( query )
