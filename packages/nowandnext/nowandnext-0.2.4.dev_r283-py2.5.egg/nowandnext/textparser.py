import re

class textparser(object):
    """
    Extracts dictionaries of key: value pairs from blocks of text.
    """
    RE_MATCH_LINE = re.compile( r"""^(?P<key>[a-zA-Z0-9_\-\.]+): *(?P<value>[a-zA-Z0-9@ \-_\./:]+)$""" )

    def __init__(self):
        pass

    def parse(self, input_text ):
        for textline in input_text.split('\n'):
            match_results = self.RE_MATCH_LINE.search( textline )
            if match_results:
                matchgroups = match_results.groupdict()
                yield matchgroups['key'], matchgroups['value']
            else:
                print "Not matched: %s" % textline

    def parsetodict( self, input_text ):
        return dict( a for a in self.parse( input_text ) )

if __name__ == "__main__":
    text="""hello:goodbye
next:fun
email:sal@stodge.org
web: http://blog.stodge.org
site: http://www.hootingyard.org
sample: this is a message with spaces"""
    foo = textparser()
    print foo.parsetodict( text )
