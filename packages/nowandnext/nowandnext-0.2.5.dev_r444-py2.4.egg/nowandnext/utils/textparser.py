import re
import logging

log = logging.getLogger(__name__)

class textparser(object):
    """
    Extracts dictionaries of key: value pairs from blocks of text.
    """
    RE_MATCH_LINE = re.compile( r"""^(?P<key>[a-zA-Z0-9_\-\.]+):\s+(?P<value>[a-zA-Z0-9@ \-_\./:&\+]+)$""" )

    def __init__(self):
        pass

    def parse(self, input_text ):
        unmatched = []
        for textline in input_text.split('\n'):
            match_results = self.RE_MATCH_LINE.search( textline )
            if match_results:
                matchgroups = match_results.groupdict()
                yield str(matchgroups['key']).lower(), matchgroups['value']
            else:
                unmatched.append( textline )
                # print "Not matched: %s" % textline
        yield ( "unmatched", unmatched )

    def parsetodict( self, input_text ):
        return dict( a for a in self.parse( input_text ) )

    def translate( self , dictinput ):
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
    pprint.pprint( foo.parsetodict( text ) )
