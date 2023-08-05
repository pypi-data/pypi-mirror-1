### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: rss.py 49587 2008-01-20 22:31:10Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49587 $"

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

    title = u""

    subtitle = u""

    link = u""

    author = None

    id = u""

    @property
    def updated(self) :
        return IMTime(self).mtime

class Author( object ) :

    implements(IAuthor)

    author_name = u""

    author_email = u""

AuthorTupleWidget = CustomWidgetFactory(
       TupleSequenceWidget,
       subwidget=CustomWidgetFactory(
       ObjectWidget,
       Author))
