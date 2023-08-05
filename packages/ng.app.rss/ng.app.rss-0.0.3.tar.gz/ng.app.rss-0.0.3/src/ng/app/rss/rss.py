### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: rss.py 49721 2008-01-24 23:21:17Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49721 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IRSS,IAuthor
from persistent import Persistent
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget
from ng.adapter.mtime.interfaces import IMTime

# TODO: От перзистент должен пораждатся. И хорошо бы в класс вписать
# умолчания всех переменных реализуюемого им интерфейса
                
class RSS( Persistent ) :

    implements(IRSS)

    def __init__(self,*kv,**kw) :
        super(RSS,self).__init__(*kv,**kw)
        self.author = ()


    title = u""

    subtitle = u""

    link = u""

    author = None

    id = u""

    @property
    def updated(self) :
        return IMTime(self).strftime("%Y-%m-%dT%H-%M-%SZ")

class Author( Persistent ) :

    implements(IAuthor)

    author_name = u""

    author_email = u""

AuthorTupleWidget = CustomWidgetFactory(
       TupleSequenceWidget,
       subwidget=CustomWidgetFactory(
       ObjectWidget,
       Author))
