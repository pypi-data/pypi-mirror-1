# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License 

import datetime
from utils import pydt
from utils import dt2int
from utils import utc

DSTADJUST = 'adjust'
DSTKEEP   = 'keep'
DSTAUTO   = 'auto'

def recurringSequence(start, delta, end, dst=DSTAUTO):
    """a sequence of integer objects.
    
    @param start: a python datetime (non-naive) or Zope DateTime.
    @param delta: integer >=0 (unit is minutes) or None.
    @param end: a python datetime (non-naive) or Zope DateTime >=start or None.
    @param dst: is either DSTADJUST, DSTKEEP or DSTAUTO. On DSTADJUST we have a 
                more human behaviour on daylight saving time changes: 8:00 on 
                day before spring dst-change plus 24h results in 8:00 day after 
                dst-change, which means in fact one hour less is added. On a 
                delta < 24h this will fail!
                If DSTKEEP is selected, the time is added in its real hours, so
                the above example results in 9:00 on day after dst-change.
                DSTAUTO uses DSTADJUST for >=24h and DSTKEEP for < 24h deltas.                
    
    @return: a sequence of dates
    """        
    start = pydt(start)
       
    if delta is None or delta < 1 or end is None:
        yield start
        return
    
    assert(dst in [DSTADJUST, DSTKEEP, DSTAUTO])
    if dst==DSTAUTO and delta<24*60:
        dst = DSTKEEP
    elif dst==DSTAUTO:
        dst = DSTADJUST
        
    end = pydt(end)    
    delta = datetime.timedelta(minutes=delta)
    yield start
    before = start
    while True:
        after = before + delta
        if dst==DSTADJUST:
            after = after.replace(tzinfo=after.tzinfo.normalize(after).tzinfo)
        else:
            after = after.tzinfo.normalize(after)
        if utc(after) > utc(end):
            break        
        yield after
        before = after

def recurringIntSequence(start, delta, end, dst=DSTAUTO):
    """same as recurringSequence, but returns integer represetations of dates.
    """ 
    for dt in recurringSequence(start, delta, end, dst):
        yield dt2int(dt)
        
    
    
    
    
    
    