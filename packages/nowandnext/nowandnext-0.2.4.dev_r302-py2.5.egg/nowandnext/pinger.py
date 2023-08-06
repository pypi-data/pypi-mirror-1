"""
A script to provide now & next information for the streaming service.
By Salim Fadhley
sal@stodge.org
"""
import logging
import datetime
import optparse
import pkg_resources
import sys
import os
import ConfigParser
import Queue
import datetime
import socket
import time

from nowandnext.utc import utc
from nowandnext.calQuery import CalQuery, CalendarException
from nowandnext.scheduleevent import scheduleevent
from nowandnext.schedulegap import schedulegap
from nowandnext.simplecast import simplecast
from nowandnext.detectos import osinfo
from gdata.service import RequestError

from gdata.service import BadAuthentication

log = logging.getLogger( __name__ )

class pinger( object ):
    MAX_EVENTS_TO_LOAD=6
    SOCKET_ERROR_SLEEP_TIME=30
    configfilename = "resonance_pinger.cfg"

    @classmethod
    def getConfigFileLocation( cls ):
        configdir = osinfo.get_config_dir( "Pinger" )
        configfilepath = os.path.join( configdir, cls.configfilename )
        return configfilepath

    @classmethod
    def mkParser( cls ):
        parser = optparse.OptionParser()
        defaultconfigfilelocation = cls.getConfigFileLocation( )
        parser.add_option( "--configfile", dest="configfilepath",
                           help="The location of the configuration file, default is: %s" % defaultconfigfilelocation,
                           default=defaultconfigfilelocation, type="str" )

        parser.add_option( "--quiet", "-q", dest="verbose",
                           help="Make the logging less verbose",
                           default=True, action="store_false" )

        parser.add_option( "--warpfactor", "-w", dest="warpfactor",
                           help="Make time appear to go faster - handy for debugging the script but never for production use.",
                           default=1.0, type="float" )
        
        parser.add_option( "--debugmode", "-d", dest="debugmode",
                           help="Crash out on critical failure.",
                           default=False, action="store_true" )

        return parser

    def __init__( self, config, warpfactor ):
        self.systemtime = datetime.datetime.now()
        self.utctime = datetime.datetime.now( utc )
        log.info("Pinger utility started at %s (%s utc)" % ( self.systemtime, self.utctime ) )

        self._warpfactor = warpfactor
        if os.path.exists( config ) and os.path.isfile( config ):
            self._config = self.loadConfig( config )
            log.info( "Loaded config from %s" % config )
        else:
            log.warn("Config file is missing!")
            configdir, configfilename = os.path.split( config )
            if not os.path.exists( configdir ):
                os.makedirs( configdir )
                log.warn( "New confiuration directory %s made." % configdir )
            if not os.path.exists( config ):
                default_config = pkg_resources.resource_string(__name__, 'data/resonance_pinger.cfg.example')
                file( config , "w" ).write( default_config )
                log.warn( "Default configuration written to %s, please edit it!" % configdir )
            sys.exit("Please configure the application by editing the script at: %s" % config )

        self._calargs=( self._config.get('pinger','account'),
                        self._config.get('pinger','password'),
                        self._config.get('pinger','calendar_name'), )

        scsettings = ( self._config.get('simplecast','host', 'localhost'),
                       int( self._config.get('simplecast','port', 8181) ) )

        try:
            self._default_artist = self._config.get( "pinger", "default_artist" )
            self._default_website = self._config.get( "pinger", "default_website" )
            self._default_title = self._config.get( "pinger", "default_title" )
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
                self.getEvents( event_queue, )

    def getEvents(self, evqueue, includeCurrent=False ):
        """
        Fill up the event queue with events
        """
        now = datetime.datetime.now( utc )
        onehour = datetime.timedelta( seconds = ( 60 * 60 ) )
        sometimeago = now - ( onehour * 1 )
        sometimeinthefuture = now + ( onehour * 24 )

        try:
            self._cal = foo = CalQuery( *self._calargs )
            eventInstances = [a for a in self._cal.getEventInstances( sometimeago , sometimeinthefuture )]
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
            log.warn("Calendar could not be loaded!")
            time.sleep( self.SOCKET_ERROR_SLEEP_TIME )
            return
        
        eventList = []
        
        if includeCurrent==True:
            currentEvents = [ a for a in eventInstances if a.isNow( now ) ]
            for ce in currentEvents:
                eventList.append( ce )

        futureEvents = [ a for a in eventInstances if a.isFuture( now ) ][:self.MAX_EVENTS_TO_LOAD]

        futureEventInstances = [ a for a in futureEvents ]
        for futureEvent in futureEventInstances:
            eventList.append( futureEvent )
        
        scheduleEventList = [ scheduleevent(a, default_artist=self._default_artist, default_website=self._default_website, ) for a in eventList ]
        eventListWithGaps = self.insertGaps( now, scheduleEventList )
        
        for ev in eventListWithGaps:
            evqueue.put( ev )
            
    def insertGaps(self, now, eventlist ):
        newlist = []
        
        assert type(now) == datetime.datetime
        assert type(eventlist) == list
        for event in eventlist:
            assert type(event) == scheduleevent
        
        if len(eventlist) == 0:
            return eventlist
        
        if eventlist[0].getStartTime() > now:
            newlist.append( schedulegap( now, eventlist[0].getStartTime(), default_artist=self._default_artist, default_title=self._default_title, default_website=self._default_website ) )
        
        for evpointer in xrange( 0, len( eventlist ) ):
            thisEvent = eventlist[ evpointer ]
            newlist.append( thisEvent )
            
            try:
                nextEvent = eventlist[ evpointer + 1 ]
                thisEventEnds = thisEvent.getEndTime()
                nextEventStarts = nextEvent.getStartTime()

                if thisEvent.getEndTime() <  nextEvent.getStartTime():
                    newlist.append( schedulegap( thisEventEnds , nextEventStarts, default_artist=self._default_artist, default_title=self._default_title, default_website=self._default_website ) )
            except IndexError, ie:
                break

        return newlist
            
        
    
    def processEvent(self, ev ):
        """
        Do something with the event
        """
        ev.run( simplecast=self._simplecast, warpfactor=self._warpfactor )

    def loadConfig( self, configfilepath ):
        configdir, configfilename = os.path.split( configfilepath )
        assert os.path.exists( configfilepath ) and os.path.isfile( configfilepath )
        config = ConfigParser.SafeConfigParser()
        configfile = file( configfilepath )
        config.readfp( configfile, configfilename )
        return config

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

    print "This product is released under the GPL"
    print "Source code is here: http://code.google.com/p/suxtools/source/browse"
    print "For latest packaged release: http://pypi.python.org/pypi/nowandnext/"
    print "Or just type: easy_install -U nowandnext"
    print "For tech support contact sal@stodge.org"
    print "Or m. 07973 710 574"
    print "(c) 2008 Salim Fadhley"

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