import datetime

from nowandnext.calendar.gdate import gdatetime
from nowandnext.timezones.utc import utc

class Geventinstance( object ):
    """
    """
    EVENT_TYPE = "unknown"
    
    def __init__(self, eventinstance, event ):
        self._eventinstance = eventinstance
        self._event = event

    def getEvent(self):
        return self._event

    def getStart(self, tz=utc ):
        return gdatetime.fromisoformat( self._eventinstance.start_time, tz )

    def getEnd( self, tz=utc ):
        return gdatetime.fromisoformat( self._eventinstance.end_time, tz )

    def isNow(self, comptime, tz=utc ):
        if self.getStart( tz ) <= comptime < self.getEnd( tz ):
            return True
        return False

    def isFuture(self, comptime, tz=utc ):
        if self.getStart( tz ) >= comptime:
            return True
        return False

    def isPast( self, comptime, tz=utc ):
        if self.getEnd( tz ) <= comptime:
            return True
        return False
    
    def __hash__(self):
        return hash( self.getStart() ) + hash( self.getEvent() )
    
    def __eq__(self, other):
        try:
            assert isinstance( other, self.__class__ )
            assert other.getEvent() == self.getEvent( )
            assert other.getStart() == self.getStart( utc )
            assert other.getEnd() == self.getEnd( utc )
            return True
        except AssertionError, ae:
            return False

    def __gt__( self, other ):
        assert isinstance( other, self.__class__ )
        try:
            assert self.getStart() > other.getStart()
            return True
        except AssertionError, ae:
            return False

    def __lt__( self, other ):
        assert isinstance( other, self.__class__ )
        try:
            assert self.getStart() < other.getStart()
            return True
        except AssertionError, ae:
            return False

    def __str__(self):
        if self.getStart().date() == self.getEnd().date():
            strep = """%s @%s-%s""" % ( self.getEvent().getTitle(),
                                        self.getStart().strftime("%d/%m/%y %H:%M"),
                                        self.getEnd().strftime("%H:%M") )
        else:
            strep = """%s @%s-%s""" % ( self.getEvent().getTitle(),
                                        self.getStart().strftime("%d/%m/%y %H:%M"),
                                        self.getEnd().strftime("%d/%m/%y %H:%M" ) )
        return strep

    def __repr__(self):
        return """<%s.%s %s>""" % ( self.__class__.__module__,
                                    self.__class__.__name__,
                                    str(self), )


