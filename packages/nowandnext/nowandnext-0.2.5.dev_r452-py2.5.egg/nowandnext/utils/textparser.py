import re
import logging

log = logging.getLogger(__name__)

class textparser(object):
    """
    Extracts dictionaries of key: value pairs from blocks of text.
    """
    RE_MATCH_LINE = re.compile( r"""^(?P<key>[a-zA-Z0-9_\-\.]+):\s+(?P<value>[a-zA-Z0-9@ \-_\./:&\+]+)$""" )
    RE_MATCH_TITLE = re.compile( "^(?P<title>.+)\s*(?P<repeat>\(\s*repeat\s*\))\s*$", re.I + re.U )
    
    
    def __init__(self):
        pass

    @classmethod
    def parse(cls, input_text ):
        unmatched = []
        for textline in input_text.split('\n'):
            match_results = cls.RE_MATCH_LINE.search( textline )
            if match_results:
                matchgroups = match_results.groupdict()
                yield str(matchgroups['key']).lower(), matchgroups['value']
            else:
                unmatched.append( textline )
                # print "Not matched: %s" % textline
        yield ( "unmatched", unmatched )

    @classmethod
    def parsetodict( cls, input_text, title="" ):
        
        match_title = cls.RE_MATCH_TITLE.search( title )
        
        result = dict( a for a in cls.parse( input_text ) )
        
        if match_title:
            if match_title.groupdict()["repeat"]:
                result["repeat"]=True
            else:
                result["repeat"]=False
            result["title"]=match_title.groupdict()["title"]
        else:
            result["repeat"]=False
            result["title"]=title

        return result

    @staticmethod
    def translate( dictinput, ):
        dictoutput={}
        
        
        
        for keyname in [ 'artist', 'artists', 'producer', 'producers', 'presenter', 'presenters', 'host', 'hosts' ]:
            if dictinput.has_key( keyname ):
                dictoutput['artist'] = dictinput[ keyname ]
                
        for keyname in [ 'picture', 'logo', 'artwork', 'emblem', 'icon', ]:
            if dictinput.has_key( keyname ):
                dictoutput['picture'] = dictinput[ keyname ]
                
        for keyname in ['web', 'email' ]:
            try:
                val = dictinput.get( keyname )
                dictoutput['keyname'] = val
            except KeyError, ke:
            
                log.debug("Not matched: %s" % keyname )
                

        dictoutput.update(dictinput)
        return dictoutput

if __name__ == "__main__":
    text=u"""hello:goodbye
next: fun
email: sal@stodge.org
web: http://blog.stodge.org
site: http://www.hootingyard.org
sample: this is a message with spaces
presenters: Josh & Boo
artists: BARRY + NIGEL
version: Version 2.0
myspace: http://www.stage4.co.uk/5050
web: http://www.stage4.co.uk/5050
presenters: Jah Beef & Papa Milo
MaGiC Time: Ignore this item
MaGiCTimE: fun
http://www.foo.net
blah
bloo 
ningi
"""
    foo = textparser()
    import pprint
    pprint.pprint( foo.parsetodict( text, "Hooting Yard (repeat ) " ) )
    pprint.pprint( foo.parsetodict( text, "Hooting Yard " ) )
