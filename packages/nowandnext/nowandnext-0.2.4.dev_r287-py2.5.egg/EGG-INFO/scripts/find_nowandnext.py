"""
A script to provide now & next information for the streaming service.
By Salim Fadhley
sal@stodge.org
"""
import logging
import datetime
import nowandnext
import optparse
from nowandnext.calQuery import CalQuery
import math
import sys
import os
import traceback

log = logging.getLogger(__name__)

ONEMINUTE = datetime.timedelta( seconds=60 )
ONEHOUR = ONEMINUTE * 60
ONEDAY = ONEHOUR * 24

def mkparser( ):
    parser = optparse.OptionParser()

    DEFAULT_USERNAME = os.environ.get("CAL_USERNAME", "sal@stodge.org" )
    DEFAULT_PASSWORD = os.environ.get("CAL_PASSWORD", "xxxx", )
    DEFAULT_CALENDAR = os.environ.get("CAL_FEEDNAME", "Resonance Schedule" )

    parser.add_option( "-u", "--username", dest="username",
                       default=DEFAULT_USERNAME )

    parser.add_option( "-s", "--schedule", dest="schedule",
                       default=DEFAULT_CALENDAR )

    parser.add_option( "-p", "--password", dest="password",
                       default=DEFAULT_PASSWORD )

    return parser


def deltaToString( mytd ):
    seconds = mytd.seconds
    minutes = math.floor( seconds / 60.0 )
    hours = math.floor( minutes / 60.0 )

    assert type(mytd) == datetime.timedelta
    if mytd > ONEDAY:
        return "See Website for details."
    elif mytd > ONEHOUR:
        if hours == 1:
            return "in one hour"
        else:
            return "in %i hours" % hours
    elif mytd > ONEMINUTE:
        if minutes == 1:
            return "on one minute"
        else:
            return "in %i minutes" % minutes
    else:
        return "in %i seconds" % seconds


def getNowAndNext( now, username, password, schedulename ):
    foo = CalQuery( username, password, schedulename )

    endTime = now + ( CalQuery.D1H * 12 )
    startTime = now - ( CalQuery.D1H * 4 )

    log.debug( "Now: %s, End: %s" % ( now, endTime ) )

    eventInstances = [a for a in foo.getEventInstances( startTime , endTime )]

    currentEvents = [ a.getEvent() for a in eventInstances if a.isNow( now ) ]
    futureEvents = [ a.getEvent() for a in eventInstances if a.isFuture( now ) ]
    pastEvents = [ a.getEvent() for a in eventInstances if a.isPast( now ) ]

    if len( currentEvents ) == 0:
        currentEvent = None
    else:
        currentEvent = currentEvents[0]

    if len( futureEvents ) == 0:
        nextEvent = None
    else:
        nextEvent = futureEvents[-1:][0]

    return [ currentEvent, nextEvent, ]

def initialCap( strin ):
    return strin[0:1].upper() + strin[1:]

def main( ):
    timenow = datetime.datetime.now()
    logging.basicConfig()
    log.setLevel(logging.INFO )

    options, args = mkparser().parse_args()

    nowShow, nextShow = getNowAndNext( timenow, options.username, options.password, options.schedule )

    nextDelta = [ a for a in nextShow.getInstances() ][0].getStart() - timenow
    strNextShowStart = deltaToString( nextDelta )

    if nowShow:
        output = "Now: %s." % nowShow.getTitle()
    else:
        output = ""

    if nextShow:
        output = output + "%s: %s." % ( initialCap( strNextShowStart ), nextShow.getTitle() )
    else:
        output = output + "See http://www.resonancefm.com for schedule."

    return output

if __name__ == "__main__":
    print "Content-type: text/plain\n"
    print main()
    sys.exit(0)
