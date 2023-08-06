"""
Some handy time-periods.
"""
import datetime

SECONDS_IN_A_MINUTE = 60
SECONDS_IN_AN_HOUR = SECONDS_IN_A_MINUTE * 60
SECONDS_IN_A_DAY = SECONDS_IN_AN_HOUR * 24

onesecond = datetime.timedelta( seconds=1 )
oneminute = onesecond * SECONDS_IN_A_MINUTE
onehour = oneminute * SECONDS_IN_A_MINUTE
oneday = datetime.timedelta( days=1 )
oneweek = oneday * 7
