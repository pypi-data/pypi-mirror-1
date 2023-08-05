### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: rssview.py 49683 2008-01-23 14:24:08Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49683 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from ng.app.objectqueue.interfaces import IObjectQueue
from ng.app.rss.interfaces import IRSS,IRSSEntry
from zope.app import zapi
from zope.component import queryMultiAdapter

class RSSView(object) :
    
    # Тута адаптируем контекст к IObjectQueue
    # Тута к rss
    # Атрибутики rss проксируем на адаптированный RSS
    # Рисуем один атрибутик который возвращает entries, хавая содержимое из IObjectQueue.values()
    # и приводя его к IRSSEntry. Адаптера пока нет и не нужно пока
    # А потом пишем pt-файл

    """ RSSView
    """    
    
    @property
    def entries(self):
        """ Рисуем один атрибутик который возвращает entries, хавая содержимое из IObjectQueue.values()
        """
        return ( x for x in (
            queryMultiAdapter((y,self.request),IRSSEntry,default=None)
            for y in IObjectQueue(self.context).values() ) if x is not None)

    @property
    def rss(self):
        return IRSS(self.context)
