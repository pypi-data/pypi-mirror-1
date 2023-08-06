"""
Generate an RSS feed of the schedule.
"""
import PyRSS2Gen
import datetime
import sys
import logging
from nowandnext.utils.cmdline import cmdline
from nowandnext.utils.detectos import osinfo
from nowandnext.timezones.utc import utc
from nowandnext.calendar import periods
from nowandnext.calendar.scheduleevent import scheduleevent
from nowandnext.calendar.calQuery import CalQuery, NoCalendarEntry
from nowandnext.utils.textparser import textparser
from nowandnext.timezones.uk import uk as timezone_uk

log = logging.getLogger( __name__ )

class schedule_to_rss( cmdline ):
    
    def __init__(self, configfilepath ):
        self._config = self.getconfiguration(configfilepath)
        self._calargs=( self._config.get('pinger','account'),
                        self._config.get('pinger','password'),
                        self._config.get('pinger','calendar_name'), )
        
        self.default_website = self._config.get("feed", "link")
        
        
    def calendaritemtorssitem(self, calendaritem ):
        scheduleitem = scheduleevent( calendaritem, default_website=self._config.get("feed", "link") ) 
        query = textparser.translate( textparser.parsetodict( calendaritem.getEvent().getDescription() ) ) 
        
        description = "\n".join( query["unmatched"] )
        
        item = PyRSS2Gen.RSSItem(
             title = scheduleitem.getTitle(),
             link = query.get("web", self.default_website ),
             description = description,
             guid = scheduleitem.getGuid(),
             pubDate = scheduleitem.getStartTime( tz=timezone_uk ) )
        return item
        
    def __call__(self):
        calendaritems = self.getcalendaritems()
        
        rss = PyRSS2Gen.RSS2(
            title = self._config.get("feed", "title"),
            link = self._config.get("feed", "link"),
            description = self._config.get("feed", "description"),    
            lastBuildDate = datetime.datetime.now(),
            items = [ self.calendaritemtorssitem( a ) for a in calendaritems ] )
        
        rss.write_xml( sys.stdout, encoding="utf-8" )
        
    def getcalendaritems(self):
        now = datetime.datetime.now( utc )
        sometimeinthefuture = now + ( periods.onehour * 24 )

        cal = CalQuery( *self._calargs )
        eventinstances = []
        
        try:
            eventinstances.append( cal.getCurrentEventInstance( now ) )
        except NoCalendarEntry:
            log.warn("There is no calendar entry for now.")
        
        eventinstances.extend( [a for a in cal.getEventInstances( now , sometimeinthefuture ) if a not in eventinstances ] )
        
        return eventinstances

def main( ):
    logging.basicConfig()
    options, args = schedule_to_rss.mkParser().parse_args()
    if options.verbose:
        logging.getLogger("").setLevel(logging.INFO)
    else:
        logging.getLogger("").setLevel(logging.WARN)
    
    os_spesific_handler = osinfo.get_logger("Pinger")
    os_spesific_handler.setLevel( logging.WARN )
    logging.getLogger("").addHandler( os_spesific_handler )

    # schedule_to_rss.copyrightmessage()

    s2r = schedule_to_rss( options.configfilepath )
    s2r()
    
if __name__ == "__main__":
    main()
    