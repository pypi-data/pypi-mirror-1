# Thank's to plone4artists calendar

import datetime
from DateTime import DateTime

try:
    import dateutil
except ImportError:
    print ImportError

def gettz(name=None):
    try:
        return _extra_times[name]
    except KeyError:
        return dateutil.tz.gettz(name)

def dt2DT(dt, tzname=None):
    """Convert a python datetime to DateTime. 

    >>> import time, os
    >>> oldtz = os.environ['TZ']
    >>> os.environ['TZ'] = 'Brazil/East'
    >>> time.tzset()
    >>> brt = gettz('Brazil/East')

    No timezone information, assume local timezone at the time.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0))
    DateTime('2005/11/07 18:00:00 GMT-2')

    Provide a default TZID:

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0), tzname='EET')
    DateTime('2005/11/07 18:00:00 GMT+2')

    UTC timezone.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0, tzinfo=gettz('UTC')))
    DateTime('2005/11/07 18:00:00 GMT+0')

    BRST timezone (GMT-2 on this day).

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0, tzinfo=brt))
    DateTime('2005/11/07 18:00:00 GMT-2')

    BRT timezone (GMT-3 on this day).

    >>> dt2DT(datetime.datetime(2005, 07, 07, 18, 0, 0, tzinfo=brt))
    DateTime('2005/07/07 18:00:00 GMT-3')
    
    Change back:
    >>> os.environ['TZ'] = oldtz
    >>> time.tzset()    

    """
    if tzname is None and dt.tzinfo is None:
        # Assume local time
        tz = gettz()
    elif tzname is not None:
        # Convert to timezone
        tz = gettz(tzname)
    else:
        tz = None
    if tz is not None:
        dt = dt.replace(tzinfo=tz)
    return DateTime(dt.isoformat())

