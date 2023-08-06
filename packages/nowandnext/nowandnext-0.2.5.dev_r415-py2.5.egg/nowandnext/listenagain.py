import sched
import itertools

class ListenAgain( object ):
    
    CONFIG_FILE_NAME = "resonance_listenagain.cfg"
    
    EVENTS_TO_LOAD = 5
    
    REPEAT_STRING = "(repeat)"
    
    def __init__(self):
        """
        """
        
        # Load & Validate configuration (like in Pinger)
        
        # Set up a blank scheduler
        self._scheduler = None
        
    def __call__(self):
        """
        """
        self.reloadSchedule( )
        self._scheduler.run()    
            
            
    def reloadSchedule( self ):
            # Load N events into the scheduler
            
            # Make a new connection to Google Claendar with Calquery, using the settings we loaded earlier.
        
            # Load N events from Google Calendar
            for loadedeventinstance in self.filterEvents( loadedevents ):
                # Add the event to the scheduler with the relevant additional settings from the configfile.
                
                # Create an object that we will execute at the appropriate time from the scheduler
                archiver_instance = archiver( gcalevent, parking_folder, recording_stream )
                
                self._scheduler.addevent( archiver_instance, startTime = gcalevent.getStart() ) 
                
            self._scheduler.addevent( self.getEndOfSequenceTime( loadedevents ), self.reloadSchedule() )
    
    def filterEvents( self, eventSequence ):
        return itertools.ifilter( self.filterevent, eventSequence )
    
    def filterevent(self, theEventInstance ):
        """
        Returns true if this is an event we are going to record.
        """
        if self.REPEAT_STRING in theEventInstance.getEvent().getTitle():
            return False
        return True
            