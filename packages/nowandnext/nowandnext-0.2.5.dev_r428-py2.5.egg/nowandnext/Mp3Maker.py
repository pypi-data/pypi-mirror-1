import urllib
import sys
import datetime
import logging
import cStringIO
import os
import socket

#from mutagen.id3 import ID3, TIT2
# from tagger import *
log = logging.getLogger( __name__ )

class RecordingError( Exception ):
    """
    Something bad happened during recording.
    """

class Mp3Maker:
    """
    A class of utilities to record from shoutcast & icecast streams to local files on the hard disk.
    """
    BUFFERSIZE = 65535
    MAX_BUFFERSIZE = BUFFERSIZE * 16
    
    @classmethod
    def applyTag (cls, file):
        #mp3 = ID3(file)
        #mp3.add(TIT2(encloding=3, text="An example of res recording"))
        #mp3.save(file)
        mp3 = ID3v2(file)
        mp3.version
        for frame in mp3.frames:
            print frame.fid 
        
        
        
    @classmethod
    def RecordMp3 ( cls, url, duration, outfile ):
        """
        Record the output of a shoutcast stream for a period of time.
        @param url: The complete shoutcast URL where the stream can be obtained.
        @type url: str
        @param duration: The duration to record for.
        @type duration: datetime.timedelta
        @param out_filepath: A file to write to
        @type out_filepath: file-like object
        """
        # Do some validation here:
        assert type(url) == str, "Url should be a string"
        assert url.startswith("http"), "Url needs to start wtith http"
        assert type(duration) == datetime.timedelta
        assert duration > datetime.timedelta()
        
        starttime = datetime.datetime.now()
        endtime = starttime + duration
        
        mp3data = urllib.urlopen( url )
        memorybuffer = cStringIO.StringIO()
        
        try:
            while ( datetime.datetime.now() < endtime ):
                # print "time now ->" + str((time.time() -starttime))
                
                try:
                    memorybuffer.write( mp3data.read( cls.BUFFERSIZE ) )
                except socket.error, se:
                    raise RecordingError( "Error during recording %s" % repr(se) )
                
                if len( memorybuffer.getvalue() ) >= cls.MAX_BUFFERSIZE:
                    bufferout.write( memorybuffer.getvalue() )
                    # Reset memorybuffer
                    memorybuffer.truncate( 0 )
            
        finally:
            lastData = memorybuffer.getvalue()
            bufferout.write( lastData )
            
        
 
                
    
    #while 1:
    def __init__(self, secs, out_filename):
        pass
    
if __name__ == "__main__":
    """
    A small function to test this class
    """
    import tempfile
    logging.basicConfig()
    bufferout = tempfile.NamedTemporaryFile( suffix=".mp3" )    
    result = Mp3Maker.RecordMp3( url = 'http://icecast.commedia.org.uk:8000/resonance_hi.mp3', 
                                 duration = datetime.timedelta(seconds=10), 
                                 outfile = "/home/james/jt.mp3")
    outfile = bufferout 
    log.warn( "Sample file saved to %s" % bufferout.name )
        
    #    Mp3Maker.applyTag('/home/james/develop/james.mp3')
    
    log.warn('actually finished ')
    bufferout.close()
    
    #result = Mp3Maker.RecordMp3( url = 'http://icecast.commedia.org.uk:8000/resonance_hi.mp3', 
    #                             duration = datetime.timedelta(seconds=10), 
    #                             outfile = "/home/james/develop/james2.mp3" )
    
    #log.warn('actually finished 2')
    
    

