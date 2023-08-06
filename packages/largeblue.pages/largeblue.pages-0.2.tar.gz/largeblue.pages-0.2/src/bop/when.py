#!/usr/local/env/python
#############################################################################
# Name:         bop
# Purpose:      Time related functions
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import random, pytz
from datetime import datetime
import zope.interface
from zope.dublincore.interfaces import IZopeDublinCore
from zope.publisher.browser import TestRequest
from zope.security.proxy import removeSecurityProxy

from bebop.protocol import protocol
import interfaces


def now():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

def testdatetime(year=None, month=None, day=None, hour=None, minutes=None):
    if year is None:
        year = random.randint(2000, 2005)
    if month is None:
        month = random.randint(10, 12)
    if day is None:
        day = random.randint(5, 21)
    if hour is None:
        hour = random.randint(8, 21)
    if minutes is None:
        minutes = random.randint(0, 59)
    return datetime(year, month, day, hour, minutes)

class DateFormatter(object):
    """Help formatter."""
    def __init__(self, context):
        self.context = context
        
    def format(self, t, *args, **kw):
        if t is None :
            return u"--"
        return self.context.format(t, *args, **kw)
        
def formatter(request=None):
    if request is None:
        request = TestRequest()
    locale = request.locale.dates.getFormatter('dateTime', 'medium')
    return DateFormatter(locale)
                   
def dateLabel(date, request=None):
    """Returns the day part of datetime object in a readable manner.
    
    >>> t = datetime.utcnow()
    >>> t1 = t - datetime.timedelta(days=1)
    >>> page = HTMLPage(None, TestRequest())
    
    >>> page.dateLabel(t1)
    u'Yesterday'

    
    """
    if date is None :
        return ""
    
    t = datetime.utcnow()
    if t.year == date.year:
        if t.month == date.month:
            if t.day == date.day:
                return u'Today'
            if t.day-1 == date.day:
                return u'Yesterday'
            return u'This month'
        return formatter(request).format(date, "MMMM")        
    return formatter(request).format(date, "MMMM yyyy")
    
def formatMonth(month, request=None):
    date = datetime(2000, month, 1)
    return formatter(request).format(date, "MMMM")

def formatDay(date, request=None):
    """ Returns the day part of datetime object."""
    if date is None :
        return ""
    return formatter(request).format(date, "d. MMMM yyyy")

def formatTime(datetime, request=None):
    """ Returns the time part of datetime object in a readable manner. """
    if datetime is None :
        return ""
    return formatter(request).format(datetime, "d. MMMM yyyy")

timestamp = protocol.GenericFunction('ITimestamp')
"""Returns a datetime timestamp for sorting etc. that is guaranteed to exist."""

@timestamp.when(None)
def default_timestamp(obj):
    dc = IZopeDublinCore(obj, None)
    if dc is not None:
        return dc.effective or dc.modified or dc.created or now()
    return now()    

def ispublished(obj, t=None):
    dc = IZopeDublinCore(obj, None)
    if dc is None or dc.effective is None:
        return False
#    print "ispublished", [dc.effective, dc.expires]
    if t is None:
        t = now()
    if t < dc.effective:
        return False
    if dc.expires is not None and t > dc.expires:
        return False
    return True

class Published(protocol.Adapter):
    """Questions related to publication dates."""    

    def getEffective(self):
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            return dc.effective
        return None

    def setEffective(self, when):
        dc = IZopeDublinCore(self.context)
        if when is None :
            try :
                dc = removeSecurityProxy(dc)
                del dc._mapping[u'Date.Effective']
            except KeyError :
                pass
        else :
            dc.effective = when

    effective = property(getEffective, setEffective)
    published = property(getEffective, setEffective)

    def getExpires(self):
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            return dc.expires
        return None
        
    def setExpires(self, when):    
        dc = IZopeDublinCore(self.context)
        if when is None :
            try :
                dc = removeSecurityProxy(dc)
                del dc._mapping[u'Date.Expires']
            except KeyError :
                pass
        else :
            dc.expires = when
            
    expires = property(getExpires, setExpires)


class When(Published):
    """Questions related to temporal aspects."""
    
    zope.interface.implements(interfaces.IWhen)
    protocol.adapter(None, permission='zope.Public')

    @property
    def when(self):   
        return timestamp(self.context)    
   
    @property
    def created(self):   
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            return dc.created
        return None

    @property
    def modified(self):   
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            return dc.modified
        return None
        
            