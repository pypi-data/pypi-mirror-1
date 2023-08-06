### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51555 2008-08-30 22:59:06Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51555 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, URI, Tuple, Float
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema import Object
                

class IAuthor (Interface) :
      
      author_name = TextLine(
                       title = u'author_name',
                       description = u'author_name',
                       default = u'',
                       required = False)

      author_email = TextLine(
                       title = u'author_email',
                       description = u'author_email',
                       default = u'',
                       required = False)

class IRSSAdd(Interface) :
      title = TextLine(
        title = u'Title',
        description = u'Title',
        default = u'',
        required = False)

      subtitle = TextLine(
        title = u'Subtitle',
        description = u'Subtitle',
        default = u'',
        required = False)

      link = URI(
        title = u'URL',
        description = u'URL',
        required = True)

      author = Tuple(title=u'authors',
                    description=u'Some authors',
                    required=False,
                    value_type=Object(title=(u'author'),
                                      description=(u'...'),
                                      schema=IAuthor,
                                     )
                   )
                   

                                                                
      id = TextLine(
        title = u"id",
        description = u"id",
        )

class IRSS(IRSSAdd) :
      """ """
      updated = TextLine(
        title = u"Updated",
        description = u"Last modification time ",
        readonly = True,)

class IRSSEntry (Interface) :
      ### TODO: ЭТо видимо относится к интерфейсу ентри в ленте. Давай
      ### заведем отдельный интерфейс IRSSEnter и свалим их все туда и пока
      ### забудем про них - добъемя вначеале пустых лент

      entry_title = TextLine(
                       title = u'entry_title',
                       description = u'entry_title',
                       default = u'',
                       required = False)

      entry_link = URI(
        title = u'URL',
        description = u'URL',
        required = True)

      entry_id = TextLine(
        title = u"entry_id",
        description = u"entry_id",
        )

      entry_updated = Datetime(
        title = u"Date of updated",
        description = u"Date of updated")

      entry_summary  = TextLine(
                       title = u'entry_summary',
                       description = u'entry_summary',
                       default = u'',
                       required = False)