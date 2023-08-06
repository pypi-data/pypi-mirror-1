# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License 

import pytz
import datetime
import logging
logger = logging.getLogger('DateRecurringIndex.utils')

utctz = pytz.timezone('UTC')

def guesstz(DT):
    """'Guess' pytz from a zope DateTime.
    
    !!! theres no real good method to guess the timezone.
    DateTime was build somewhere in 1998 long before python had a working 
    datetime implementation available and still stucks with this incomplete 
    implementation.
    """
    if DT.timezoneNaive():
        return utctz
    tzname = DT.timezone()
# this might be needed with zope2.10 (different pytz version)
#    if tzname.startswith('GMT'):
#        tzname = 'Etc/%s' % tzname
    try:
        tz = pytz.timezone(tzname)
        return tz
    except KeyError:
        pass
    return None
    

def pydt(dt):
    """converts a zope DateTime in a python datetime.
    """
    if dt is None:
        return None

    if isinstance(dt, datetime.datetime):
        return dt.replace(tzinfo=dt.tzinfo.normalize(dt).tzinfo)

    tz = guesstz(dt)
    if tz is None:
        dt = dt.toZone('UTC')
        tz = utctz
                
    year, month, day, hour, min, sec = dt.parts()[:6]
    # seconds (parts[6]) is a float, so we map to int
    sec = int(sec)
    dt = datetime.datetime(year, month, day, hour, min, sec, tzinfo=tz)
    dt = dt.tzinfo.normalize(dt)
    return dt 

def utc(dt):
    """convert python datetime to UTC."""
    if dt is None:
        return None 
    return dt.astimezone(utctz)
    
def dt2int(dt):
    """calculates an integer from a datetime.

    resolution is one minute, always relative to utc    
    """
    if dt is None:
        return 0
    dt = utc(dt)
    value = (((dt.year*12+dt.month)*31+dt.day)*24+dt.hour)*60+dt.minute
    return value
    
