import re

from nowandnext.utils.textparser import textparser

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
        
    def __add__( self, other ):
        assert isinstance( other, ErrorReport )
        newreport = ErrorReport( )
        newreport._errorlist.extend( self._errorlist )
        newreport._errorlist.extend( other._errorlist )
        return newreport
        
    def getErrorText(self):
        return "\n".join( e[0] for e in self._errorlist )
    
    def getErrorHTMLList(self):
        listlines = ["<li>%s</li>" % a[0] for a in self._errorlist ]
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
        
        self._subtests = subtests
        for subtest in subtests:
            assert isinstance( subtest, BaseErrorDetector ), "Only a instance of BaseErrorDetector can be a subtest of this class: %s" % self.__class__.__name__
        
    def test( self, calendarobject ):
            """
            Redefine this method elsewhere
            """
            return True
        
    def getFailPoints(self):
        return self.FAIL_POINTS
        
    def __call__( self, calendarobject ):
        report = ErrorReport()
    
        try:
            result = self.test( calendarobject )
        except CalendarError, ce:
            report.append(  ",".join(str(a) for a in ce.args) , self.getFailPoints() )
            
        if report.isOk():
            for subtest in self._subtests:
                report += subtest( calendarobject )
            
        assert isinstance( report, ErrorReport ), "Report should be an ErrorReport, got %s" % repr( report )
        return report

class DetectNoDescription( BaseErrorDetector ):
    FAILPOINTS = 10
    
    def test( self, item ):
        
        try:
            desc = item.getDescription()
        except Exception, e:
            import pdb
            pdb.set_trace()
        
        if len(desc) == 0:
            raise CalendarError("The description was empty - please add some description text for this item.")
        
        if len(desc) < 25:
            raise CalendarError("The description '%s' seems very short - please add more detail." % desc )
        
class DetectNoWebLink( BaseErrorDetector ):
    
    def test( self, item ):
        tp = textparser()
        resultdict = tp.parsetodict( item.getDescription() )
                
        if not "web" in resultdict.keys():
            raise CalendarError("No correctly listed web-site was in the description. Please add one so that listners know where to find information. Web-sites should be prefixed with the prefix 'web:'")

class DetectNoEmail( BaseErrorDetector ):
    
    def test( self, item ):
        tp = textparser()
        resultdict = tp.parsetodict( item.getDescription() )
        
        if not "email" in resultdict.keys():
            raise CalendarError("No contact email address was provided for this show. Please list one using the prefix 'email:'.")

class DetectWebUnmatched( BaseErrorDetector ):
    
    def test( self, item ):
        tp = textparser()
        resultdict = tp.parsetodict( item.getDescription() )
        
        for line in resultdict["unmatched"]:
            if "http://" in line:
                raise CalendarError("It looks that the item contains a website which is not listed on a new-line with the prefix 'web:' : %s" % line )


DetectErrorsInEvent = BaseErrorDetector( 
                            DetectNoDescription(
                                    DetectNoWebLink(),
                                    DetectWebUnmatched(),
                                                ),
                                         )

if __name__ == "__main__":
    foo = 1
    print repr( DetectErrorsInEvent( foo ) )