#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Jens Klein <jens@bluedynamics.com>"""              
__docformat__ = 'plaintext'

import datetime
import calendar

def CWof(date):
    """the calendar week number of a date.
    
    @param date: python datetime
    """
    return date.isocalendar()[1]       

def firstDayOfCW(year, cw, tzinfo=None):
    """first day of a numbered calendar week.
    
    @param year: year where the week is of (int)
    @param cw: calendar week (int).
    """
    # thx to Peter Otten, base found at 
    # http://mail.python.org/pipermail/python-list/2004-May/264156.html
    day = datetime.datetime(year, 2, 1, tzinfo=tzinfo)
    year, weekBase, dayBase = day.isocalendar()
    day += datetime.timedelta(1 - dayBase + (cw - weekBase)*7)
    return day

def daysOfWeek(year, kw, tzinfo=None):
    # thx to Peter Otten, base found at 
    # http://mail.python.org/pipermail/python-list/2004-May/264156.html
    day = firstDayOfCW(year, kw, tzinfo) 
    delta = datetime.timedelta(1)
    for i in range(6):
        yield day
        day += delta
    yield day        

def numberOfDaysInYear(dt):
    if dt.isLeapYear(): 
        return 366
    return 365

def numberOfDaysInMonth(dt):
    firstday, numdays = calendar.monthrange(dt.year, dt.month) 
    return numdays
        
def daysOfMonth(year, month, tzinfo=None):
    day = datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=tzinfo)
    numdays = numberOfDaysInMonth(day)
    delta = datetime.timedelta(1)
    for i in range(numdays-1):
        yield day
        day += delta
    yield day 

def hoursOfDay(year, month, day, tzinfo=None):
    hour = datetime.datetime(year, month, day, 0, 0, 0, tzinfo=tzinfo)        
    delta = datetime.timedelta(0, 3600)
    for i in range(23):
        yield hour
        hour += delta
    yield hour 

def isSameDay(start, end):
    if start.day == end.day and \
       start.month == end.month and \
       start.year == end.year:
        return True
    return False
