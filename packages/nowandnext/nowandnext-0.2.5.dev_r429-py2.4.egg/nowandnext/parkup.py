#####################################################################
# archiver.py module
# for www.archive.org classes
# please do not use yet - this is work in progress 
#
# jctt 5th June 2008 - 6th June 2008
# james@tregaskis.org
#
# added the pinger functionality to read in from Google calendar
# needs refactoring to remove common functions in pinger.py
# Work still in progress!
# (not working at the moment gone to a funeral today)
#####################################################################
import logging
import datetime
import optparse
from ftplib import FTP
import ftplib
import os
import traceback
import pkg_resources
from nowandnext.timezones.utc import utc
from elementtree.ElementTree import Element, SubElement, ElementTree as ET
from tagger import *
import ConfigParser
from nowandnext.detectos import osinfo
import time
import socket
import Queue
from nowandnext.calendar.calQuery import CalQuery, CalendarException, NoCalendarEntry
from nowandnext.calendar.scheduleevent import scheduleevent
from nowandnext.calendar.schedulegap import schedulegap
from nowandnext.simplecast import simplecast
from nowandnext.utils.detectos import osinfo
from gdata.service import RequestError
from gdata.service import BadAuthentication

log = logging.getLogger( __name__ )

class archiver:
    MAX_EVENTS_TO_LOAD=6
    SUFFIX_METADATA = "_meta.xml"
    SUFFIX_FILES = "_files.xml"
    CONFIG_FILE_NAME = "resonance_archiver.cfg"
    #WEB_STORE_URL = "www.tregaskis.org"
    WEB_STORE_URL = "ia311342.us.archive.org"
    
    instance = None
    
    
    
    #def __init__(self, username, password):
    def __init__(self, config, warpfactor):

        self.systemtime = datetime.datetime.now()
        self.utctime = datetime.datetime.now( utc )
        log.info("archiver utility started at %s (%s utc)" % ( self.systemtime, self.utctime ) )

        self._warpfactor = warpfactor
        if os.path.exists( config ) and os.path.isfile( config ):
            self._config = self.loadConfig( config )
            log.info( "Loaded config from %s" % config )
        else:
            log.warn("Config file is missing!")
            configdir, configfilename = os.path.split( config )
            if not os.path.exists( configdir ):
                os.makedirs( configdir )
                log.warn( "New configuration directory %s made." % configdir )
            if not os.path.exists( config ):
                default_config = pkg_resources.resource_string(__name__, 'data/resonance_archiver.cfg.example')
                file( config , "w" ).write( default_config )
                log.warn( "Default configuration written to %s, please edit it!" % configdir )
            sys.exit("Please configure the application by editing the script at: %s" % config )

        self._calargs=( self._config.get('archiver','account'),
                        self._config.get('archiver','password'),
                        self._config.get('archiver','calendar_name'), )

        scsettings = ( self._config.get('simplecast','host', 'localhost'),
                       int( self._config.get('simplecast','port', 8181) ) )

        try:
            self._username = self._config.get( "archiver", "username" ) 
            self._password = self._config.get( "archiver", "password" )
            self._default_artist = self._config.get( "archiver", "default_artist" )
            self._default_website = self._config.get( "archiver", "default_website" )
            self._default_title = self._config.get( "archiver", "default_title" )
            self._default_logo = self._config.get( "archiver", "default_logo" )
        except ConfigParser.NoOptionError, noe:
            log.critical( noe[0] )
            log.warn("Please edit your configuration file.")
            sys.exit(1)

        #log.info("Connecting to SimpleCast server %s:%i" % scsettings )
        #self._simplecast = simplecast( *scsettings )
     
    # set up config file
    @staticmethod
    def getConfigFileLocation( configfilename ):
        configdir = osinfo.get_config_dir( "Archiver" )
        configfilepath = os.path.join( configdir, configfilename )
        return configfilepath    
    
    @staticmethod
    def loadConfig( configfilepath ):
        configdir, configfilename = os.path.split( configfilepath )
        assert os.path.exists( configfilepath ) and os.path.isfile( configfilepath )
        config = ConfigParser.SafeConfigParser()
        configfile = file( configfilepath )
        config.readfp( configfile, configfilename )
        return config
    
    @classmethod
    def mkParser( cls ):
        parser = optparse.OptionParser()
        defaultconfigfilelocation = cls.getConfigFileLocation( cls.CONFIG_FILE_NAME )
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
    
    #test data for dictionary key value pairs for metatdata xml file
    MetaDataSettings={"identifier":"Wavelength2008-05-27B", 
        "collection":"Wavelength Show On Resonance 104.4 FM www.resonancefm.com", 
        "title":"Wavelength",
        "subject":" ",
        "mediatype":"etree",
        "year":"2008",
        "publicdate":"2008-06-27 19:30:00",
        "creator":"William English",
        "description":"William English is joined by various coughing guests for a chat",
        "coverage":" ",
        "md5s":"",
        "date":"2008-06-10 08:20:ss",
        "uploader":"James Tregaskis",
        "addeddate":"",
        "adder":"",
        "pick":"",
        "updateddate":"",
        "updater":"",
        "notes":"",
        "source":"original",
        "lineage":"",
        "venue":"www.ResonanceFm.com",
        "stream_only":"0",
        "discs":"",
        "has_mp3":"1",
        "shndiscs":"2",
        "public":"1",
        "collection":"etree",
        "publisher":"",
        "taper":"",
        "transferer":"",
        "runtime":"30:00",
        "format":"128bps MP3",
        "licenseur1":"http://creativecommons.org/licenses/by/2.0/uk/"}
    
    #@classmethod
    def outerUpload(self, dict_metadata, ):
        # this takes care of uploading the files including xml files
        #MyHomeMovie/
        #MyHomeMovie/MyHomeMovie_files.xml
        #MyHomeMovie/MyHomeMovie_meta.xml
        #MyHomeMovie/MyHomeMovie.mpeg
        self.writeMetadataXml(dict_metadata)
        self.writeFileXml(dict_metadata)
        print "creating ftp directory ...."
        self.makeDirectory(dict_metadata.get("identifier"))
        print "uploading metadata.xml file ...."
        self.uploadFile(dict_metadata.get("identifier"),"/home/james/workspace/trunk/src/nowandnext/" + dict_metadata.get("identifier") + self.SUFFIX_METADATA)
        print "uploading fles.xml file ...."
        self.uploadFile(dict_metadata.get("identifier"),"/home/james/workspace/trunk/src/nowandnext/"+ dict_metadata.get("identifier") + self.SUFFIX_FILES )
        print "uploading mp3 file ...."
        self.uploadFile(dict_metadata.get("identifier"),"/home/james/workspace/trunk/src/nowandnext/"+ dict_metadata.get("identifier") + ".mp3" )
        
    @classmethod
    def writeFileXml(self, dict_metadata):
        try:
            files = Element("files")
            file = SubElement(files,'file')
            file.attrib["name"]=dict_metadata.get("identifier")
            file.attrib["source"]='original'
            runtime = SubElement(file,'runtime')
            runtime.text = dict_metadata.get("runtime")
            format = SubElement(file,'format')
            format.text = dict_metadata.get("format")
                
                
            ET(files).write("/home/james/workspace/trunk/src/nowandnext/" + dict_metadata.get("identifier") + self.SUFFIX_FILES , encoding='UTF-8')
        except:
            traceback.print_exc()

    # the filename is the fully qualified path of file
    # needs some refactoring to reduce code    
    @classmethod
    def writeMetadataXml( self, dict_metatdata ):
        try:
            _metadata = Element("metadata")
            identifier = SubElement(_metadata,"identifier")
            identifier.text = dict_metatdata.get("identifier")
            mediatype = SubElement(_metadata,'mediatype')
            mediatype.text = dict_metatdata.get("mediatype")
            collection = SubElement(_metadata, "collection")
            collection.text = dict_metatdata.get("collection")
            title = SubElement(_metadata,"title")
            title.text = dict_metatdata.get("title")
            subject = SubElement(_metadata,"subject")
            subject.text = dict_metatdata.get("subject")
            year = SubElement(_metadata,"year")
            year.text = dict_metatdata.get("year")
            publicdate= SubElement(_metadata, "publicdate")
            publicdate.text = dict_metatdata.get("publicdate")
            creator = SubElement(_metadata, "creator")
            creator.text = dict_metatdata.get("creator")
            description = SubElement(_metadata, "description")
            description.text = dict_metatdata.get("description")
            coverage = SubElement(_metadata, "coverage")
            coverage.text = dict_metatdata.get("coverage")
            md5s = SubElement(_metadata, "md5s")
            md5s.text = dict_metatdata.get("md5s")
            date = SubElement(_metadata, "date")
            date.text = dict_metatdata.get("date")
            uploader = SubElement(_metadata, "uploader")
            uploader.text = dict_metatdata.get("uploader")
            addeddate = SubElement(_metadata, "addeddate")
            addeddate.text = dict_metatdata.get("addeddate")
            pick = SubElement(_metadata, "pick")
            pick.text = dict_metatdata.get("pick")
            updateddate = SubElement(_metadata, "updateddate")
            updateddate.text = dict_metatdata.get("updateddate")
            adder = SubElement(_metadata, "adder")
            adder.text = dict_metatdata.get("adder")
            updater = SubElement(_metadata, "updatater")
            updater.text = dict_metatdata.get("updater")        
            notes = SubElement(_metadata, "notes")
            notes.text = dict_metatdata.get("notes")
            lineage = SubElement(_metadata, "lineage")
            lineage.text = dict_metatdata.get("lineage")        
            venue = SubElement(_metadata, "venue")
            venue.text = dict_metatdata.get("venue")
            stream_only = SubElement(_metadata, "stream_only")
            stream_only.text = dict_metatdata.get("stream_only")
            discs = SubElement(_metadata, "discs")
            discs.text = dict_metatdata.get("discs")
            has_mp3 = SubElement(_metadata, "has_mp3")
            has_mp3.text = dict_metatdata.get("has_mp3")
            shndiscs = SubElement(_metadata, "shndiscs")
            shndiscs.text = dict_metatdata.get("shndiscs")
            public = SubElement(_metadata, "public")
            public.text = dict_metatdata.get("public")
            publisher = SubElement(_metadata, "publisher")
            publisher.text = dict_metatdata.get("publisher")
            taper = SubElement(_metadata, "taper")
            taper.text = dict_metatdata.get("taper")
            transferrer = SubElement(_metadata, "transferrer")
            transferrer.text = dict_metatdata.get("transferrer")
            licenseur1 = SubElement(_metadata.get, "licenseur1")
            licenseur1.text = dict_metatdata.get("licenseur1")
             
            ET(_metadata).write( "/home/james/workspace/trunk/src/nowandnext/" + dict_metatdata.get("identifier")+ self.SUFFIX_METADATA, encoding='UTF-8')
        except:
            traceback.print_exc()
                
    @classmethod
    def makeDirectory(self, filename):
        print 'logging in '
        ftp= ftplib.FTP()
        ftp.connect(self.WEB_STORE_URL, '')
        print ftp.getwelcome()
        print '---------------'
        try:
            try:
                # get the file name out to change to directory
                #fullname = filetosend
                #name = os.path.split(fullname)[1]
                
                print 'in try block'
                ftp.login(archiver.instance._username, archiver.instance._arch_password)
                print 'logged in'
                print 'currently in ' + ftp.pwd()
                
                ftp.mkd(filename)
                #ftp.quit()
            except:
                print "************************************************"
                traceback.print_exc()
        finally:
            ftp.quit()
        
        
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
    

                            
    @classmethod
    def uploadFile (self, filename, filetosend):
        print 'logging in '
        ftp= ftplib.FTP()
        ftp.connect(self.WEB_STORE_URL, '')
        print ftp.getwelcome()
        print '---------------'
        try:
            try:
                fullname = filetosend
                # get the file name out to change to directory
                name = os.path.split(fullname)[1]
                print 'in try block'
                ftp.login(archiver.instance._username, archiver.instance._password)
                print 'logged in'
                
                ftp.cwd('/' + filename )
                print 'currently in ' + ftp.pwd()
                
                f = open(fullname, "w+")
                ftp.storbinary('STOR ' + name, f)
                f.close()
                print "ok stored " + name
                print "Files:"
                print ftp.retrlines('LIST')
                #ftp.quit()
            except:
                traceback.print_exc()

        finally:
            print "Quitting..."
            ftp.quit()

            #session=ftplib.FTP('85.233.160.70', 'tregaskis.org', 'trouble')
            #f=open(filetosend,'rb')
            #session.storbinary('STOR metadata.xml',f)
            #f.close()
            #session.quit()
        
            print ('finished ftp')
    
    @classmethod
    def tester ( self ):
        archiver.instance.writeMetadataXml(archiver.instance.MetaDataSettings)
        archiver.instance.writeFileXml(archiver.instance.MetaDataSettings)

    @classmethod
    def iter (self):
        keys= self.MetaDataSettings.keys()
        for x in keys:
                print x, "-->", self.MetaDataSettings[x]
CRITICAL_FAILURE_SLEEP_TIME = 60    

def main(  ):
    logging.basicConfig()
    options, args = archiver.mkParser().parse_args()
    if options.verbose:
        logging.getLogger("").setLevel(logging.INFO)
    else:
        logging.getLogger("").setLevel(logging.WARN)        
    os_spesific_handler = osinfo.get_logger("Archiver")
    os_spesific_handler.setLevel( logging.WARN )
    logging.getLogger("").addHandler( os_spesific_handler )

    print "This product is released under the GPL"
    print "Documentation is here: http://code.google.com/p/suxtools/wiki/Archiver"
    print "To Exit: CTRL-Break or CTRL-C"
    print "Or just type: easy_install -U nowandnext"
    print "For tech support contact sal@stodge.org or james@tregaskis.org"
    

    myarchiver = archiver( options.configfilepath, options.warpfactor )
    
    while True:
        try:
            return myarchiver()
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
            
############################################################################
##username and password to be included here
##x=archiver( "tregaskis.org", "xxxxx"  )
#x=archiver( "info@tregaskis.org", "sl0rty"  )
#x.tester
#x.instance.tester()
#x.instance.tester()
#x.instance.uploadFile('/home/james/workspace/trunk/src/nowandnext/mymetadata.xml')
#x.instance.uploadFile('/home/james/workspace/trunk/src/nowandnext/mymetadata.xml')
#MetaDataSettings={"identifier":"Wavelength2008-05-27B", 
#    "collection":"Wavelength Show On Resonance 104.4 FM www.resonancefm.com", 
#    "title":"Wavelength",
#    "subject":"Radio Programme",
#    "mediatype":"etree",
#    "year":"2008",
#    "publicdate":"2008-06-27 19:30:00",
#    "creator":"William English",
#    "description":"William English is joined by various coughing guests for a chat",
#    "coverage":" ",
#    "md5s":"",
#    "date":"2008-06-10 08:20:ss",
#    "uploader":"James Tregaskis",
#    "addeddate":"",
#    "adder":"",
#    "pick":"",
#    "updateddate":"",
#    "updater":"",
#    "notes":"",
#    "source":"original",
#    "lineage":"",
#    "venue":"www.ResonanceFm.com",
#    "stream_only":"0",
#    "discs":"",
#    "has_mp3":"1",
#    "shndiscs":"2",
#    "public":"1",
#    "collection":"etree",
#    "publisher":"",
#    "taper":"",
#    "transferer":"",
#    "runtime":"30:00",
#    "format":"128bps MP3",
#    "licenseur1":"http://creativecommons.org/licenses/by/2.0/uk/"}

#x.instance.outerUpload(MetaDataSettings)

#x.iter()
#x.uploadFile('/home/james/workspace/trunk/src/nowandnext/mymetadata.xml' )
#x.uploadFile('/home/james/workspace/trunk/src/nowandnext/myFileData.xml' )

