### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"
 
from ng.content.annotation.annotationswitcher.interfaces import IAnnotationSwitcher
from ng.content.annotation.dictannotation.interfaces import IDictAnnotationAble
from ng.content.annotation.eventannotation.interfaces import IEventAnnotationAble
from ng.content.annotation.productannotation.interfaces import IProductAnnotationAble

class IAnnotationSwitcherDict(IAnnotationSwitcher,IDictAnnotationAble) :
    """Use as dictionary """

class IAnnotationSwitcherEvent(IAnnotationSwitcher,IEventAnnotationAble) :
    """Use as Event """

class IAnnotationSwitcherProduct(IAnnotationSwitcher,IProductAnnotationAble) :
    """Use as Product """

