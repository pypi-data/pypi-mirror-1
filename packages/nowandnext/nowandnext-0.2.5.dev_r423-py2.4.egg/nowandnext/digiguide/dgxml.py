import elementtree.ElementTree as ET
from nowandnext.calendar.convert import timedelta_to_minutes

class dgxmlfeed( object ):
    def __init__(self, channels=None ):
        assert type(channels) == list
        
        self.oldestStart = None
        self.newestEnd = None
        self.itemCount = 0
        self._xml = ET.Element("channels")
        
        if channels == None:
            channels = []
            
        for channel in channels:
            self._xml.append( channel )
            
    @classmethod
    def program(cls, scheduleitem=None ):
        xml = ET.Element("program")
        
        xml.attrib["name"] = scheduleitem.getTitle()
        xml.attrib["startdate"] = scheduleitem.getStartTime().strftime("%Y/%m/%d")
        xml.attrib["starttime"] = scheduleitem.getStartTime().strftime("%H%M")
        
        td_duration = scheduleitem.getEndTime() - scheduleitem.getStartTime()
        mins_duration = timedelta_to_minutes( td_duration )
        
        xml.attrib["duration"] = str( mins_duration )
        
        synopsis = ET.Element("synopsis")
        synopsis.text = scheduleitem.getDescription()
        
        xml.append( synopsis )
        
        return xml
        
            
    @classmethod
    def channel( cls, name, programs=None ):
        if programs==None:
            programs = []
        
        assert type(programs) == list
        
        xml = ET.Element("channel")
        xml.attrib["name"] = name
        
        x_programs = ET.Element("programs")
        xml.append( x_programs )
        
        for program in programs:
            x_programs.append( program )
            
        return xml

    def dump( self, thefile ):
        """
        Write out the digiguide XML to a file.
        """
        
        tree = ET.ElementTree( self._xml )
        tree.write( thefile, encoding="iso8859-1" )

    def dumps( self ):
        return
    
if __name__ == "__main__":
    import sys
    foo = dgxmlfeed( [ dgxmlfeed.channel("ResonanceFM"), ] )
    foo.dump( sys.stdout )
