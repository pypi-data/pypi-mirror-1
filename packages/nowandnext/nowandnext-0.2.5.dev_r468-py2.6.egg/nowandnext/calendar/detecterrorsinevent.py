import re
import socket
import dns.resolver
import urlparse
import httplib
import socket

from nowandnext.utils.textparser import textparser

class dummy_parse_result(object):
    pass

class CalendarError( Exception ):
    pass

class ErrorReport( object ):
    def __init__( self ):
        self._errorlist = []
    
    def append( self, errortext, errorscore ):
        assert type(errortext) == str
        assert type(errorscore) == int
        assert errorscore >= 0
        self._errorlist.append( ( errortext, errorscore, ) )
        
    def getErrorCount(self):
        return len( self._errorlist )
    
    def getTotalPoints(self):
        return sum( a[1] for a in self._errorlist )
        
    def __add__( self, other ):
        assert isinstance( other, ErrorReport )
        newreport = ErrorReport( )
        newreport._errorlist.extend( self._errorlist )
        newreport._errorlist.extend( other._errorlist )
        return newreport
        
    def getErrorText(self):
        return "\n".join( e[0] for e in self._errorlist )
    
    def getErrorHTMLList(self):
        listlines = ["<li>%s (%i points)</li>" % (a[0], a[1]) for a in self._errorlist ]
        if len( listlines ) > 0:
            listlines.append("<li><strong>Total error score: %i</strong></li>" % self.getTotalPoints() )
        return "<ul>\n%s\n</ul>" % "\n".join( listlines )
        
    
    def getErrorScore(self):
        return sum( e[1] for e in self._errorlist )
    
    def isOk(self):
        if len( self._errorlist ) > 0:
            return False
        else:
            return True

class BaseErrorDetector( object ):
    FAIL_POINTS = 2
    
    def __init__(self, *subtests ):
        
        self.fail_score = self.FAIL_POINTS
        self._subtests = subtests
        for subtest in subtests:
            self.fail_score += subtest.getFailPoints()
            assert isinstance( subtest, BaseErrorDetector ), "Only a instance of BaseErrorDetector can be a subtest of this class: %s" % self.__class__.__name__
        
        
    def test( self, calendarobject ):
            """
            Redefine this method elsewhere
            """
            return True
        
    def getFailPoints(self):
        return self.fail_score
        
    def getTestObject( self, input ):
        return input
        
    def __call__( self, inputobject ):
        report = ErrorReport()
    
        try:
            testobject = self.getTestObject( inputobject )
            self.test( testobject )
        except CalendarError, ce:
            report.append(  ",".join(str(a) for a in ce.args) , self.getFailPoints() )
            
        if report.isOk():
            for subtest in self._subtests:
                report += subtest( testobject )
            
        assert isinstance( report, ErrorReport ), "Report should be an ErrorReport, got %s" % repr( report )
        return report

class DetectNoDescription( BaseErrorDetector ):
    FAILPOINTS = 10
    
    def getTestObject(self, input ):
        try:
            return input.getDescription()
        except Exception, _:
            raise CalendarError("Could not get the description data for this item, please check it manually")
    
    def test( self, item ):
        if len( item ) == 0:
            raise CalendarError("The description was empty - please add some description text for this item.")
        
        if len( item ) < 25:
            raise CalendarError("The description '%s' seems very short - please add more detail." % item )

class DetectParsable( BaseErrorDetector ):
    FAILPOINTS = 10
    
    def getTestObject(self, input ):
        try:
            tp = textparser()
            return tp.translate( tp.parsetodict( input ) )
        except Exception, _:
            raise CalendarError("Completely failed to parse the text- could not make any sense of it.")
    

class DetectInvalidChars( BaseErrorDetector ):
    FAILPOINTS = 5
    
    def test( self, item ):
        try:
            converted = item.encode("ascii")
        except UnicodeEncodeError, ue:
            raise CalendarError("The description contained non-ASCII text. It was probably cut & pasted from word. This will confuse non unicode-aware RSS readers." )

class DetectNoWebLink( BaseErrorDetector ):
    FAIL_POINTS = 5
    
    def getTestObject(self, input ):
        try:
            return input["web"]
        except KeyError, _:
            raise CalendarError("No correctly listed web-site was in the description. Please add one so that listners know where to find information. Web-sites should be prefixed with the prefix 'web:'")
            
class DetectTitle( BaseErrorDetector ):
    FAIL_POINTS = 5
    
    def getTestObject(self, input ):
        try:
            return input.getTitle()
        except KeyError, _:
            raise CalendarError("This item does not have a valid title.")
        
    def test( self, item ):
        try:
            assert len(item) > 0, "Title seems to be missing"
            assert len(item) > 5, "This title seems very short: %s" % item
            assert len(item) < 256, "This title seems to be very long, %i chars" % len(item)
            
            if "repeat" in item.lower():
                assert "(repeat)" in item.lower(), 'The repeat flag should be written as "(Repeat)".'
        except AssertionError, ae:
            raise CalendarError( ae[0] )
    


class DetectBadWebLink( BaseErrorDetector ):
    FAIL_POINTS = 5
    
    MATCH_WEBSITES = re.compile("^((ht|f)tp(s?)\:\/\/|~/|/)?([\w]+:\w+@)?([a-zA-Z]{1}([\w\-]+\.)+([\w]{2,5}))(:[\d]{1,5})?((/?\w+/)+|/?)(\w+\.[\w]{3,4})?((\?\w+=\w+)?(&\w+=\w+)*)?")
    
    def test( self, item ):        
        try:
            assert len(item.strip()) > 0, "There was a 'web:' link but no actual url was provided."
            assert len(item.strip()) > 10, "This url seems too short: %s" % item 
            assert " " not in item, "A url (web-link) should not contain spaces (%s)" % item
            assert "?" not in item, "This url (%s) looks like web-query, are you sure it's the presenter's actual home-page?" % item
            assert "#" not in item, "This url (%s) has a bookmark (#) in it - is that really needed - please link to the top of the page" % item
            result = self.MATCH_WEBSITES.search( item )
            assert result, "The supplied web-site does not look like a correctly formed url: %s" % item
        except AssertionError, e:
            raise CalendarError( e[0] )
        
class DetectLinkFunction( BaseErrorDetector ):
    FAIL_POINTS = 3
    
    found_good = set()
    
    def test( self, url ):
        
        if url in self.found_good:
            # No need to check a second time
            return
                
        try:
            _parsed = urlparse.urlparse( url )
        except KeyError, _:
            raise CalendarError( "Could not parse URL: %s" % url )

        if type(_parsed) == tuple:
            # we must be still on Python 2.4

            parsed = dummy_parse_result()
            parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment = _parsed
                        
            if ":" in parsed.netloc:
                _hn, _po = parsed.netloc.split(":")
                parsed.port = int( _po )
                parsed.hostname = _hn
            else:
                parsed.port = 80
                parsed.hostname = parsed.netloc
        else:
            parsed = _parsed

        try:
            assert parsed.scheme, "The web-link %s should start with http://" % url 
            assert parsed.scheme == "http", "The web-link %s should start with http://, got %s" % ( url, parsed.scheme )
            
            if parsed.port == None:
                port = 80
            else:
                port = parsed.port
                assert parsed.port == 80, "The %s is being served from a non-standard port (%i)." % (url, parsed.port)
            
        except AssertionError, ae:
            raise CalendarError( ae[0] )

        http_connection = httplib.HTTPConnection( parsed.hostname, port )
        
        if parsed.query:
            new_url = "%s?%s" % ( parsed.path, parsed.query )
        else:
            new_url = parsed.path
            
        try:
            http_connection.request( "HEAD", new_url )
            resp = http_connection.getresponse( )
        except socket.gaierror, e:
            raise CalendarError("Could not connect to %s - server unavailable? %s" % ( url, repr(e) ) )
        
        if resp.status == 200:
            self.found_good.add( url )
            return
        elif 300 <= resp.status < 400:
            # redirected
            raise CalendarError("It looks like the web-page %s is being redirected, got error code %i, %s - please check the website." % ( url, resp.status, resp.reason ) )
        else:
            raise CalendarError("Got a HTTP error trying to check %s:  %i, %s" % ( url, resp.status, resp.reason ) )



class DetectNoEmail( BaseErrorDetector ):
    FAIL_POINTS = 3
    
    def getTestObject( self, input ):
        try:
            return input["email"]
        except KeyError, _:
            raise CalendarError("No contact email address was provided for this show. Please list one using the prefix 'email:'.")
    
            
class DetectBadEmail( BaseErrorDetector ):
    
    re_email = re.compile( "^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$", re.I )
    
    def test( self, item ):
        email = item.strip()
        
        if email.endswith("."):
            raise CalendarError, "The address '%s' has an extra dot at the end." % email
        
        email_matched = self.re_email.search( email )
        if not email_matched:
            raise CalendarError("'%s' is not a valid email address." % email )
        
class DetectNoPresenter( BaseErrorDetector ):
    
    def getTestObject( self, input ):
        try:
            return input["artist"]
        except KeyError, ke:
            raise CalendarError("Please provide the name of the person responsible for this show using the keyword 'artist: ', 'presenter: ' or 'producer: '.")


class DetectWebUnmatched( BaseErrorDetector ):
    
    
    def test( self, item ):        
        for line in item:
            if "web:" in item:
                raise CalendarError( "Tags such as 'web:' must not be indented: %s" % line )
            if "email:" in item:
                raise CalendarError( "Tags such as 'email:' must not be indented: %s" % line )
            if "presenter:" in item:
                raise CalendarError( "Tags such as 'presenter:' must not be indented: %s" % line )
            if "http://" in line:
                raise CalendarError("Entries should only contain one web-site and it should start with 'web:' : %s" % line )

class DetectNoUnmatched( BaseErrorDetector ):
    
    def getTestObject( self, input ):
        try:
            return input["unmatched"]
        except KeyError, ke:
            raise CalendarError("There was no additional data other than the tags, please add some more detail.")
    
    def test( self, item ):
        if len( item ) == 0:
             raise CalendarError( "This item only has keyword/tag lines, please include some descriptive text about the show as well." )
            



DetectErrorsInEvent = BaseErrorDetector( 
                            DetectTitle(),
                            DetectNoDescription(
                                    DetectInvalidChars(),
                                    DetectParsable( 
                                        DetectNoWebLink( DetectBadWebLink( DetectLinkFunction(), ) ),
                                        DetectWebUnmatched(),
                                        DetectNoPresenter(),
                                        DetectNoEmail( DetectBadEmail() ),
                                        DetectNoUnmatched(),
                                                    ),
                                                ),
                                         )

if __name__ == "__main__":
    foo = 1
    print repr( DetectErrorsInEvent( foo ) )