"""
Publish a schedule update to Digiguide
"""
import logging
import optparse
import datetime

from nowandnext.calendar import periods

class dgpublish(object):

    @classmethod
    def mkparser(cls):
        """
        """
        

        parser = optparse.OptionParser()

        parser.add_option( "-s", "--startdate",
                           description="Report start date", )

        return parser

    def __init__( self, startdate, enddate ):
        """
        """
        assert type(startdate) == datetime.datetime
        assert type(enddate) == datetime.datetime
        self.startdate = startdate
        self.enddate = enddate
        
    def __call__(self):
        """
        Run the report.
        """
        

if __name__ == "__main__":
    
    # options, args = dgpublish.mkparser().parse_args()
    
    default_start_date = datetime.datetime.now()
    default_end_date = default_start_date + periods.oneweek
    return dgpublish( default_start_date, default_end_date )()