import datetime
from nowandnext.calendar import periods

def timedelta_to_seconds( td ):
    assert isinstance( td, datetime.timedelta )
    return td.days * periods.SECONDS_IN_A_DAY + td.seconds
    
def timedelta_to_minutes( td ):
    return timedelta_to_seconds( td ) / float( periods.SECONDS_IN_A_MINUTE )

if __name__ == "__main__":
    start = datetime.datetime(2008,3,1)
    end = datetime.datetime(2008,3,2)
    
    delta = end-start
    print timedelta_to_minutes( delta )