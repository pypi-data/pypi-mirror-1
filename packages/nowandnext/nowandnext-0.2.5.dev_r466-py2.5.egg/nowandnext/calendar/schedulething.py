import datetime
import logging
import time

from nowandnext.timezones.utc import utc

log = logging.getLogger(__name__)

class schedulething(object):
    DATEFORMATSTRING="%d/%m/%y %H:%M"
    SECONDS_IN_A_DAY = 60 * 60 * 24
    
    def __repr__(self):
        return """<%s.%s %s>""" % ( self.__class__.__module__,
                                    self.__class__.__name__,
                                    str(self) )
        
    def __str__(self):
        return """%s: '%s' %s to %s""" % ( self.getEventType(),
                                          self.getTitle(),
                                          self.getStartTime().strftime(self.DATEFORMATSTRING ),
                                          self.getEndTime().strftime(self.DATEFORMATSTRING) )
    
    @classmethod
    def getEventType(cls):
        return cls.EVENT_TYPE
    
    @classmethod
    def timedeltaToSeconds( cls, td ):
        assert type(td) == datetime.timedelta
        dayseconds = td.days * cls.SECONDS_IN_A_DAY
        microsecondseconds = td.microseconds / 1000000.0
        result = dayseconds + td.seconds + microsecondseconds
        assert type(result) == float
        return result
    
    def getTimeToStart(self, now=None ):
        if now == None:
            now = datetime.datetime.now( utc )
            
        assert isinstance( now, datetime.datetime )
        return self.getStartTime() - now
    
    def getTimeToEnd(self, now=None ):
        if now == None:
            now = datetime.datetime.now( utc )
        
        assert isinstance( now, datetime.datetime )
        return self.getEndTime() - now
    
    def sleep_until_event_starts(self, warpfactor=1.0, bias=0):
        bias = datetime.timedelta( seconds = bias )
        delta_to_event_start = self.getTimeToStart() + bias

        if delta_to_event_start <= datetime.timedelta():
            log.info( "%s '%s' has already started!" % ( self.getEventType(), self.getTitle() ) )
        else:
            log.info( "Next %s: '%s' starts in delta:%s, local time:%s." % ( self.getEventType(),
                                                                           self.getTitle(),
                                                                           delta_to_event_start,
                                                                           self.getStartTime().strftime("%Y/%m/%d %H:%M") ) )
            self.sleepdelta( delta_to_event_start, warpfactor=warpfactor )
            
    @classmethod
    def sleepdelta( cls, td, warpfactor=1.0 ):
        assert isinstance( td, datetime.timedelta )
        seconds = cls.timedeltaToSeconds( td ) / float( warpfactor )
        assert seconds >= 0.0, "Cannot sleep a negative amount of time!"
        log.info("Sleeping for %.2f seconds, warp-factor = %.1f" % ( seconds, warpfactor ) )
        time.sleep( seconds )
            
    def run(self, simplecast, warpfactor = 1.0 ):
        log.debug("Next %s: '%s' @ %s GMT" % ( self.getEventType(), self.getTitle(), self.getStartTime() ) )
        self.sleep_until_event_starts( warpfactor=warpfactor )
        return self.ping( simplecast )