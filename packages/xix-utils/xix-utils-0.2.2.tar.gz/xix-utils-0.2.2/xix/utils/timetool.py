"""Operations on datetime instances

$Id: timetool.py 399 2007-01-22 01:27:13Z djfroofy $
"""
from datetime import datetime
from time import mktime, strptime
import calendar

__author__ = 'Drew Smathers'
__copyright__ = 'Copyright 2005, Drew Smathers'
__revision__ = '$Revision: 399 $'

_TM_MDAY = 2

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)

# TODO further unit testing on TimeDelta instance members: second, minute, hour, etc.
class TimeDelta:
    """datetime.timedelta instances for adding seconds, minutes, hours,
    days and weeks of time to datetime instances.

    Example Usage:

    >>> from xix.utils.timetool import time_delta
    >>> from time import strptime, strftime, mktime, tzset
    >>> from datetime import datetime
    >>> t = strptime('2000-12-02', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> dt2 = dt + time_delta.day
    >>> print strftime('%Y-%m-%d', dt2.timetuple())
    2000-12-03
    >>> dt2 = dt - time_delta.day
    >>> print strftime('%Y-%m-%d', dt2.timetuple())
    2000-12-01

    """

    def __init__(self):
        self.second = self.__calc1sec()
        self.minute = self.second * 60
        self.hour = self.minute * 60
        self.day = self.__calc1day()
        self.week = self.day * 7

    def __calc1sec(self):
        dt1 = datetime.fromtimestamp(mktime(strptime('2000-01-01 00', '%Y-%m-%d %S')))
        dt2 = datetime.fromtimestamp(mktime(strptime('2000-01-01 01', '%Y-%m-%d %S')))
        return dt2 - dt1
                
    def __calc1day(self):
        dt1 = datetime.fromtimestamp(mktime(strptime('2000-01-14', '%Y-%m-%d')))
        dt2 = datetime.fromtimestamp(mktime(strptime('2000-01-15', '%Y-%m-%d')))
        return dt2 - dt1

time_delta = TimeDelta()
ONE_SECOND = time_delta.second
ONE_MINUTE = time_delta.minute
ONE_HOUR = time_delta.hour
ONE_DAY = time_delta.day
ONE_WEEK = time_delta.week

def setDayOfWeek(dtime, weekday, startsun=False):
    """Return datetime falling within same week as dtime argument
    and on the indicated weekday.
    
    Example usage:

    >>> from time import strptime, strftime, mktime, tzset
    >>> from datetime import datetime
    >>> t = strptime('2005-12-02', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> dt2 = setDayOfWeek(dt, MONDAY)
    >>> print strftime('%Y-%m-%d', dt2.timetuple())
    2005-11-28
    >>> dt2 = setDayOfWeek(dt, SATURDAY)
    >>> print strftime('%Y-%m-%d', dt2.timetuple())
    2005-12-03

    @param dtime: the datetime object to convert
    @param weekday: day of week (eg. MONDAY)
    @param startsun: True if week starts on Sunday (default is False)
    """
    if startsun:
        wday = _weekday_sunstart(weekday)
        def getweekday(dt):
            return _weekday_sunstart(dt.weekday())
    else:
        wday = weekday
        def getweekday(dt):
            return dt.weekday()
    if not dtime.weekday(): # Monday is special case
        step = (1, -1)[wday <= dtime.weekday()]
    else:
        step = (1, -1)[wday < dtime.weekday()]
    newtime = dtime
    while getweekday(newtime) != wday:
        newtime = newtime + (step * ONE_DAY)
    return newtime
    
def _weekday_sunstart(wday):
    return (wday + 1) % 7

def dayOfMonth(dtime):
    """Get the day of the month for the given datetime object.

    >>> from time import strptime, strftime, mktime, tzset
    >>> from datetime import datetime
    >>> t = strptime('2005-12-23', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> print dayOfMonth(dt)
    23
    
    @param dtime: the datetime instance
    """
    return dtime.timetuple()[_TM_MDAY]

def setDayOfMonth(dtime, domon):
    """Return a new datetime object with day of month set to domon.

    >>> from time import strptime, strftime, mktime, tzset
    >>> from datetime import datetime
    >>> t = strptime('2005-12-15', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> dt = setDayOfMonth(dt, 1)
    >>> print strftime('%Y-%m-%d', dt.timetuple())
    2005-12-01
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> dt = setDayOfMonth(dt, 23)
    >>> print strftime('%Y-%m-%d', dt.timetuple())
    2005-12-23


    @param dtime: the datetime instance
    @param domon: the day of the month
    """
    monmax = monthmax(dtime)
    if monmax < domon or domon < 1:
        raise ValueError, '%d does not fall in range for datetime %s' % \
            (domon, dtime)
    delta = domon - dayOfMonth(dtime)
    return dtime + (delta * ONE_DAY)

_MONTH_PAIRS = zip(range(1,13) +  [12] + range(1,12), [12] + range(1,12) + range(1,13))
    
def incrementMonth(dtime, iterations=1):
    """Increment month for x iterations.  If iterations is less than 0, the
    datetime is decremented by one month. If the day the month of the datetime
    instance provided is the max day of the month, the resulting datetime instance
    will also end on the last day of the month.  Otherwise, the day of the month
    for the next in the iteration will be the same when possible.

    >>> from time import strptime, strftime, mktime, tzset
    >>> from datetime import datetime
    >>> t = strptime('2005-01-01', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> dt2 = incrementMonth(dt)
    >>> print strftime('%Y-%m-%d', dt2.timetuple())
    2005-02-01

    """
    mseqpairs = zip(range(1,13))
    step = (27, -27)[iterations < 0]
    adjstep = (1, -1)[iterations < 0]
    eom = monthmax(dtime) == dayOfMonth(dtime)
    newtime = dtime
    if eom:
        step = (1, -27)[iterations < 0]
        for i in range(abs(iterations)):
            mo = newtime.month
            newtime = newtime + step * ONE_DAY
            while (newtime.month, mo) not in _MONTH_PAIRS:
                newtime = newtime + adjstep * ONE_DAY
            mmax = monthmax(newtime)
            newtime = newtime + (mmax - dayOfMonth(newtime)) * ONE_DAY
    else:
        dom = dayOfMonth(dtime)
        for i in range(abs(iterations)):
            mo = newtime.month
            newtime = newtime + step * ONE_DAY
            while (newtime.month, mo) not in _MONTH_PAIRS:
                newtime = newtime + adjstep * ONE_DAY
            mmax = monthmax(dtime)
            tgt = (dom, mmax)[dom > mmax]
            newtime = newtime + (tgt - dayOfMonth(newtime)) * ONE_DAY
    return newtime
    

def monthmax(dtime):
    """Get the maximum day of month for datetime object.

    Example Usage
    
    >>> from time import strptime, strftime, mktime, tzset
    >>> from datetime import datetime
    >>> t = strptime('2005-12-01', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> print monthmax(dt)
    31
    >>> t = strptime('2006-02-01', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> print monthmax(dt)
    28
    >>> t = strptime('2008-02-01', '%Y-%m-%d')
    >>> dt = datetime.fromtimestamp(mktime(t))
    >>> print monthmax(dt)
    29

    @param dtime: the datetime instance
    """
    return calendar.monthrange(dtime.year, dtime.month)[-1]

def parse_time(tstamp, *formats):
    """Given a timestamp tstamp and a list of possible formats, try converting
    tstamp to a "time" object.

    >>> tstamp = '2005-11-30T23-56-21Z'
    >>> t = parse_time(tstamp, '%Y-%m-%dT%H-%M-%SZ', '%Y-%m-%dT%H:%M:%SZ')
    >>> from time import localtime, strftime
    >>> print strftime('%Y-%m-%d %H:%M:%S', localtime(t))
    2005-11-30 23:56:21
    """
    t = None
    for format in formats:
        try:
            t = mktime(strptime(tstamp, format))
        except ValueError:
            continue
    if t is None:
        raise ValueError, 'could not parse timestamp ' + tstamp + \
            ' with given formats: ' + ', '.join(formats)
    return t
 
