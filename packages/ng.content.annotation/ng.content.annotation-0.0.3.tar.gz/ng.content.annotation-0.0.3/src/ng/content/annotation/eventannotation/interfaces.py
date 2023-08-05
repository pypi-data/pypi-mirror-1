### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49034 2007-12-26 14:41:41Z corbeau $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49034 $"
 
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
        )
        
    place = TextLine(
        title = u'Place of event',
        description = u'Place of event',
        default = u'Internet',
        required = False)


eventannotationkey = u"eventannotation.eventannotation.EventAnnotation"
