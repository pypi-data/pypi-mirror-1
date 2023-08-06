import datetime
from nowandnext.calendar.gdate import gdatetime
from nowandnext.timezones.utc import utc

"""
An event in the calendar
"""
from nowandnext.calendar.geventinstance import Geventinstance

class gevent( object ):
    def __init__( self, event ):
        self._event = event

    def __repr__(self):
        return """<%s.%s %s>""" % ( self.__class__.__module__, self.__class__.__name__, str(self) )

    def __str__(self):
        return self.getTitle()
    
    def __eq__(self, other):
        try:
            assert isinstance( other, self.__class__ )
            assert self.getTitle() == other.getTitle()
            assert hash( self ) == hash( other )
            return True
        except AssertionError, ae:
            return False

    def __hash__( self ):
        return hash( tuple( self.getLinks() ) )

    def getInstances(self):
        for gei in self._event.when:
            yield Geventinstance( gei, self )

    def getTitle(self):        
        txttitle = self._event.title.text.strip()
        return txttitle.decode("utf8")
    
    def getLinks(self):
        return [a.href for a in self._event.link ]
    
    def getWebLink(self):
        return self.getLinks()[0]
    
    def getPublishDate(self):
        txtpubdate = self._event.published.text
        return gdatetime.fromisoformat( txtpubdate, tz=utc )

    def getDescription(self):
        txtdes = self._event.content.text
        if txtdes == None:
            txtdes = ""
        
        return txtdes.strip().decode("utf8")

    def isCurrent(self, includeTime ):
        assert type( includeTime ) in [ datetime.date, datetime.datetime, ]
        for instance in self.getInstances():
            if instance.getStart() <= includeTime <= instance.getEnd():
                return True
        return False


