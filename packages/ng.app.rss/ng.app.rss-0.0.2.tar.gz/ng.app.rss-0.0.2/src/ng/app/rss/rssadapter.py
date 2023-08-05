### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: rssadappter.py 49482 2008-01-15 19:24:29Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49482 $"

from zope.app.zapi import getUtility
from ng.app.objectqueue.interfaces import IObjectQueue
from zope.component import ComponentLookupError
from interfaces import IRSS

### 'Это, видимо, адаптер, позволяющий найти объект IRSS и вернуть его.
### Посмоттри как это сделано у ЕГора в ObjectQueue, вот тут он лежит
### objectqueue/queueutility, вот такой адаптер и нужен, только названия оставь как у тебя,
### ЕГОРа они некорректные.

def RSSAdapter(context) :
    """ """
    try :
        return getUtility(IRSS, context=context)
    except ComponentLookupError :
        print "\nCannot get utility with IRSS interface\n"
