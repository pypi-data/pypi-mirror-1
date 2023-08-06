### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EventAnnotation class for the Zope 3 based
ng.content.annotation.eventannotation package

$Id: eventannotation.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IEventAnnotation
from persistent import Persistent

class EventAnnotation(Persistent) :
    """ EventAnnotation class
    """
    implements(IEventAnnotation)

    date = None
    
    durability = u""
    
    place = u""
