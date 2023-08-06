### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.annotation.eventannotation
package

$Id: interfaces.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"


from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint


class IEventAnnotationAble(Interface) :
    """ IEventAnnotationAble interface
    """
    
    pass


class IEventAnnotation(Interface) :
    """ IEventAnnotation interface that discribe event
    """
    date = Datetime(
        title = u"Date of begining",
        description = u"Date of begining event",
        )

    # Это поле временно TextLine!!!
    durability = TextLine(
        title = u"Durability of event",
        description = u"Durability of event",
        required=False        
        )
        
    place = Text(
        title = u'Place of event',
        description = u'Place of event',
        default = u'Internet',
        required = False)


eventannotationkey = u"eventannotation.eventannotation.EventAnnotation"
