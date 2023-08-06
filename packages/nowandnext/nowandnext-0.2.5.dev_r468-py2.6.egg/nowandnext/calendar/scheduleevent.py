import datetime
import time
import logging

log = logging.getLogger( __name__ )

from nowandnext.digiguide.categories import CATEGORIES
from nowandnext.timezones.utc import utc
from nowandnext.utils.textparser import textparser
from nowandnext.calendar.schedulething import schedulething
from nowandnext.calendar.schedulegap import schedulegap

class scheduleevent( schedulething ):
    """
    A thing in the schedule that we might need to notify some other service of
    """
    EVENT_TYPE="SHOW"
    
    def __init__( self, eventinstance, default_artist="Unknown Artist", default_website="", default_logo="", default_category="ARTS" ):
        self._eventinstance = eventinstance
        self._default_artist = default_artist
        self._createtime = datetime.datetime.now( utc )
        self._default_website = default_website
        self._default_logo = default_logo
        self._default_category = default_category
        
        assert self._default_category.upper() in CATEGORIES, "%s is an invalid category. Options are: %s" % (self._default_category, ", ".join(CATEGORIES) )
        
        # log.info("New Event: %s" % eventinstance.getEvent().getTitle() )

    def __eq__( self, other ):
        try:
            assert isinstance( other, self.__class__ )
            assert self._eventinstance == other._eventinstance
            return True
        except Exception, e:
            return False

    def __hash__( self ):
        return hash( ( self.__class__, self._eventinstance ) )

    def getStartTime(self, tz=utc):
        return self._eventinstance.getStart( tz )
    
    def getEndTime(self, tz=utc):
        return self._eventinstance.getEnd( tz )

    def getTitle(self):
        return self._eventinstance.getEvent().getTitle()

    def getDescription(self):
        return self._eventinstance.getEvent().getDescription()
    
    def getGuid(self):
        return self._eventinstance.getEvent().getLinks()[0]

    def getCategory(self):
        return self.getQuery()["category"]

    def getDigiguideCategory(self):
        cat = self.getCategory().upper()
        if not cat in CATEGORIES:
            log.warn( "Invalid digiguide category: %s" % cat )
            return self._default_category.upper()
        else:
            return cat
            
            
    def getDescriptionDict(self):
        description = self.getDescription()
        tp = textparser()
        descdict = tp.translate( tp.parsetodict( description ) )
        return descdict

    def getQuery(self):
        query = {}
        now = datetime.datetime.now( utc )
        # How long till finish?
        delta_to_end = self.getTimeToEnd( now )
        seconds_to_end = self.timedeltaToSeconds( delta_to_end )

        descdict = self.getDescriptionDict()
        
        query['duration'] = seconds_to_end
        query['title'] = self._eventinstance.getEvent().getTitle()
        query['artist'] = descdict.get( 'artist', self._default_artist )
        query['website'] = descdict.get( 'web', self._default_website )
        query['picture'] = descdict.get( 'picture', self._default_logo )
        query['category'] = descdict.get( 'category', self._default_category )
        query['songtype'] = 'S'
        
        return query

            
    def ping(self, simplecast ):
        query = self.getQuery() 
        return simplecast.ping( query )
