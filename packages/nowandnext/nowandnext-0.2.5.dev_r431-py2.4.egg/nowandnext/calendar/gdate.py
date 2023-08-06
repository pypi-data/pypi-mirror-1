import datetime
import time
import re

from nowandnext.timezones.utc import utc
from nowandnext.timezones.FixedOffset import FixedOffset

class gdatetime( datetime.datetime, ):
    """
    A datetime that can construct from an isoformat
    """

    # Adapted from http://delete.me.uk/2005/03/iso8601.html
    ISO8601_REGEX = re.compile(r"(?P<year>[0-9]{4})(-(?P<month>[0-9]{1,2})(-(?P<day>[0-9]{1,2})"
        r"((?P<separator>.)(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2})(:(?P<second>[0-9]{2})(\.(?P<fraction>[0-9]+))?)?"
        r"(?P<timezone>Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?"
    )
    TIMEZONE_REGEX = re.compile("(?P<prefix>[+-])(?P<hours>[0-9]{2}).(?P<minutes>[0-9]{2})")

    ISOPADDING = "2008-04-07T14:00:00.000+00:00"
    ISOFORMAT = "%Y-%m-%dT%H:%M:%S.000+01:00$"
    @classmethod
    def fromisoformat( cls, dtisoformat, tz=None ):
        """
        Convert an isoformat into a datetime
        """
        fullisoformat = dtisoformat + cls.ISOPADDING[ len(dtisoformat): ]
        
        timematch = cls.ISO8601_REGEX.search( fullisoformat )
        
        
        timegroups = timematch.groupdict()
        
        tz = cls.parse_timezone( timegroups['timezone'] , default_timezone=tz )
        
        return cls( year = int( timegroups['year'] ),
                    month = int( timegroups['month'] ), 
                    day = int( timegroups['day'] ),
                    hour = int( timegroups['hour'] ),
                    minute = int( timegroups['minute'] ),
                    second = int( timegroups['second'] ),
                    tzinfo=tz )
    
    @classmethod
    def parse_timezone(cls, tzstring, default_timezone=utc ):
        """Parses ISO 8601 time zone specs into tzinfo offsets
        """
        if tzstring == "Z":
            return default_timezone
        if tzstring is None:
            return default_timezone
        m = cls.TIMEZONE_REGEX.match(tzstring)
        prefix, hours, minutes = m.groups()
        hours, minutes = int(hours), int(minutes)
        if prefix == "-":
            hours = -hours
            minutes = -minutes
        return FixedOffset(hours, minutes, tzstring)

if __name__ == "__main__":
    foo = gdatetime.fromisoformat( "2008-04-07T14:03:04.000+01:00"  )
    print repr(foo)
    bar = gdatetime.fromisoformat( "2007-04-07T14:03:04.000+01:00"  )

    baz = foo - bar
    print repr(baz)

