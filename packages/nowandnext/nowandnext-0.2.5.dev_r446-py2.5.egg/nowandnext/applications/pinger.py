"""
A script to provide now & next information for the streaming service.
By Salim Fadhley
sal@stodge.org
hi from jt...

"""

import logging
import datetime
import optparse
import pkg_resources
import sys
import os
import Queue
import datetime
import socket
import time

from nowandnext.timezones.utc import utc
from nowandnext.calendar.calQuery import CalQuery, CalendarException, NoCalendarEntry
from nowandnext.calendar.scheduleevent import scheduleevent
from nowandnext.calendar.schedulegap import schedulegap
from nowandnext.simplecast import simplecast
from nowandnext.utils.cmdline import cmdline
from nowandnext.utils.detectos import osinfo

from gdata.service import RequestError


from gdata.service import BadAuthentication

log = logging.getLogger( __name__ )

class pinger( cmdline ):
    MAX_EVENTS_TO_LOAD=6
    SOCKET_ERROR_SLEEP_TIME=30
    QUEUE_EMPTY_SLEEP_TIME=60


    def __init__( self, config, warpfactor ):
        self.systemtime = datetime.datetime.now()
        self.utctime = datetime.datetime.now( utc )
        log.info("Pinger utility started at %s (%s utc)" % ( self.systemtime, self.utctime ) )

        self._warpfactor = warpfactor
        
        self._config = self.getconfiguration(config)

        self._calargs=( self._config.get('pinger','account'),
                        self._config.get('pinger','password'),
                        self._config.get('pinger','calendar_name'), )

        scsettings = ( self._config.get('simplecast','host', 'localhost'),
                       int( self._config.get('simplecast','port', 8181) ) )

        try:
            self._default_artist = self._config.get( "pinger", "default_artist" )
            self._default_website = self._config.get( "pinger", "default_website" )
            self._default_title = self._config.get( "pinger", "default_title" )
            self._default_logo = self._config.get( "pinger", "default_logo" )
        except ConfigParser.NoOptionError, noe:
            log.critical( noe[0] )
            log.warn("Please edit your configuration file.")
            sys.exit(1)

        log.info("Connecting to SimpleCast server %s:%i" % scsettings )
        self._simplecast = simplecast( *scsettings )

    def __call__(self):
        event_queue = Queue.Queue()
        self.getEvents( event_queue, includeCurrent=True )
        while True:
            # The main loop
            try:
                next_event = event_queue.get( False )
                self.processEvent( next_event )
            except Queue.Empty, qe:
                time.sleep(self.QUEUE_EMPTY_SLEEP_TIME)
                self.getEvents( event_queue, includeCurrent=True )

    def getEvents(self, evqueue, includeCurrent=False ):
        """
        Fill up the event queue with events
        """
        now = datetime.datetime.now( utc )
        onehour = datetime.timedelta( seconds = ( 60 * 60 ) )
        sometimeago = now - ( onehour * 5 )
        sometimeinthefuture = now + ( onehour * 24 )

        try:
            cal = CalQuery( *self._calargs )
            eventinstances = []
            
            if includeCurrent:
                try:
                    eventinstances.append( cal.getCurrentEventInstance( now ) )
                except NoCalendarEntry:
                    log.warn("There is no calendar entry for now.")
            
            eventinstances.extend( [a for a in cal.getEventInstances( now , sometimeinthefuture )] )
        except BadAuthentication, bee:
            log.critical("Could not login to Google Calendar, please check the config file settings" )
            sys.exit()
        except RequestError, requerr:
            log.critical("Google Request Error" )
            time.sleep( self.SOCKET_ERROR_SLEEP_TIME )
            return
        except socket.gaierror, socketerror:
            log.warn("No network connection - cannot connect to Google, sleeping for %i seconds" % self.SOCKET_ERROR_SLEEP_TIME )
            time.sleep( self.SOCKET_ERROR_SLEEP_TIME )
            return
        except CalendarException, ce:
            log.exception(ce)
            log.warn("Calendar could not be loaded!")
            time.sleep( self.SOCKET_ERROR_SLEEP_TIME )
            return
        
        selectedEvents = eventinstances[:self.MAX_EVENTS_TO_LOAD]
        
        scheduleEventList = [ scheduleevent(a, default_artist=self._default_artist, default_website=self._default_website, default_logo=self._default_logo ) for a in selectedEvents ]
        eventListWithGaps = self.insertGaps( now, scheduleEventList, includeCurrent=True )
        
        for ev in eventListWithGaps:
            log.info("Enquing %s" % str(ev) )
            evqueue.put( ev )
            
    def insertGaps(self, now, eventlist, includeCurrent ):
        newlist = []
        
        assert type(now) == datetime.datetime
        assert type(eventlist) == list
        for event in eventlist:
            assert type(event) == scheduleevent
        
        if len(eventlist) == 0:
            return eventlist
        
        if includeCurrent:
            if eventlist[0].getStartTime() > now:
                newlist.append( schedulegap( now, eventlist[0].getStartTime(), default_artist=self._default_artist, default_title=self._default_title, default_website=self._default_website, default_logo=self._default_logo ) )
            
        for evpointer in xrange( 0, len( eventlist ) ):
            thisEvent = eventlist[ evpointer ]
            newlist.append( thisEvent )
            
            try:
                nextEvent = eventlist[ evpointer + 1 ]
                thisEventEnds = thisEvent.getEndTime()
                nextEventStarts = nextEvent.getStartTime()

                if thisEvent.getEndTime() <  nextEvent.getStartTime():
                    newlist.append( schedulegap( thisEventEnds , nextEventStarts, default_artist=self._default_artist, default_title=self._default_title, default_website=self._default_website, default_logo=self._default_logo ) )
            except IndexError, ie:
                break

        return newlist
    
    def processEvent(self, ev ):
        """
        Do something with the event
        """
        ev.run( simplecast=self._simplecast, warpfactor=self._warpfactor )
    

CRITICAL_FAILURE_SLEEP_TIME = 60

def main(  ):
    logging.basicConfig()
    options, args = pinger.mkParser().parse_args()
    if options.verbose:
        logging.getLogger("").setLevel(logging.INFO)
    else:
        logging.getLogger("").setLevel(logging.WARN)

    os_spesific_handler = osinfo.get_logger("Pinger")
    os_spesific_handler.setLevel( logging.WARN )
    logging.getLogger("").addHandler( os_spesific_handler )

    pinger.copyrightmessage()

    mypinger = pinger( options.configfilepath, options.warpfactor )
    
    while True:
        try:
            return mypinger()
        except KeyboardInterrupt, ke:
            log.info("User has interrupted program.")
            sys.exit(0)
        except Exception, e:
            log.exception( e )
            if options.debugmode == False:
                log.critical( "Program restarting: %s.%s" % ( e.__class__.__module__, e.__class__.__name__ ) )
                log.warn( "Sleeping for %i" % CRITICAL_FAILURE_SLEEP_TIME )
                time.sleep( CRITICAL_FAILURE_SLEEP_TIME )
            else:
                sys.exit(1)
            
if __name__ == "__main__":
    main()
