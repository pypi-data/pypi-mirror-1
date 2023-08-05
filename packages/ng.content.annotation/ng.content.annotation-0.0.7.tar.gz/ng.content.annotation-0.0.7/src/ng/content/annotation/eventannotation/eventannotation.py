### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EventAnnotation class for the Zope 3 based eventannotation package

$Id: eventannotation.py 49955 2008-02-06 20:26:35Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49955 $"

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
