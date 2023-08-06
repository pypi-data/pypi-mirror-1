import datetime

"""
An event in the calendar
"""
from nowandnext.geventinstance import Geventinstance

class gevent( object ):
    def __init__( self, event ):
        self._event = event

    def __repr__(self):
        return """<%s.%s %s>""" % ( self.__class__.__module__, self.__class__.__name__, str(self) )

    def __str__(self):
        return self.getTitle()

    def getInstances(self):
        for gei in self._event.when:
            yield Geventinstance( gei, self )

    def getTitle(self):
        return str( self._event.title.text )

    def getDescription(self):
        return str( self._event.content.text ).strip()

    def isCurrent(self, includeTime ):
        assert type( includeTime ) in [ datetime.date, datetime.datetime, ]
        for instance in self.getInstances():
            if instance.getStart() <= includeTime <= instance.getEnd():
                return True
        return False


