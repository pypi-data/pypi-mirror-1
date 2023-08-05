### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: rssadappter.py 49482 2008-01-15 19:24:29Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49482 $"

from zope.app.zapi import getUtility
from zope.component import ComponentLookupError
from zope.dublincore.interfaces import IZopeDublinCore
from zope.traversing.browser import absoluteURL

class ZDC2RSSAdapter(object) :
    """ """
    def __init__(self,context,request) :
        dc = IZopeDublinCore(context)
        self.title = dc.title
        self.updated = dc.modified
        self.summary = dc.description
        self.id = dc.Identifier
        self.link = absoluteURL(context,request)

        

