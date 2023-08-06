### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"
 
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

