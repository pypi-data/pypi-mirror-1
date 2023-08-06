#!/usr/bin/env python
import time
from datetime import datetime
TIMEFORMAT = "%m/%d/%y %H:%M:%S"

def time2str(dt=None, format=TIMEFORMAT):
    return time.strftime(format)

def datetime2str(dt=None, format=TIMEFORMAT):
    dt = dt or datetime.now()
    return dt.strftime(format)

def epoch2time(e):
    return time.gmtime(e - cst)

def epoch2str(e):
    e = epoch2time(e)
    return "%s/%s/%s %s:%s:%s" %(e.tm_year,e.tm_mon,e.tm_mday,e.tm_hour,e.tm_min,e.tm_sec)

def datetime2epoch(dt=None):
    dt = dt or datetime.now()
    return time.mktime(dt.timetuple())

def epoch2datetime(e):
    return datetime.fromtimestamp(e)
