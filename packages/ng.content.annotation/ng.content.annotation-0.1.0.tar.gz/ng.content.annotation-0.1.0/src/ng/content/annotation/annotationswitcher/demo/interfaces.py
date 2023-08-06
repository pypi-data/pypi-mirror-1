### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 52470 2009-02-07 09:25:57Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52470 $"
 
from ng.content.annotation.annotationswitcher.interfaces import IAnnotationSwitcher
from ng.content.annotation.dictannotation.interfaces import IDictAnnotationAble
from ng.content.annotation.eventannotation.interfaces import IEventAnnotationAble
from ng.content.annotation.productannotation.interfaces import IProductAnnotationAble
from ng.content.annotation.redirectannotation.interfaces import IRedirectAnnotationAble

class IAnnotationSwitcherDict(IAnnotationSwitcher,IDictAnnotationAble) :
    """Dictionary item"""

class IAnnotationSwitcherEvent(IAnnotationSwitcher,IEventAnnotationAble) :
    """Event"""

class IAnnotationSwitcherProduct(IAnnotationSwitcher,IProductAnnotationAble) :
    """Product news"""

class IAnnotationSwitcherRedirect(IAnnotationSwitcher,IRedirectAnnotationAble) :
    """Redirect"""

