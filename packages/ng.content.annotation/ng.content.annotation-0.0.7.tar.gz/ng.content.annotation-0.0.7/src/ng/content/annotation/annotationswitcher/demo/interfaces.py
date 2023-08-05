### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49955 2008-02-06 20:26:35Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49955 $"
 
from ng.content.annotation.annotationswitcher.interfaces import IAnnotationSwitcher
from ng.content.annotation.dictannotation.interfaces import IDictAnnotationAble
from ng.content.annotation.eventannotation.interfaces import IEventAnnotationAble

class IAnnotationSwitcherDict(IAnnotationSwitcher,IDictAnnotationAble) :
    """Use as dictionary """

class IAnnotationSwitcherEvent(IAnnotationSwitcher,IEventAnnotationAble) :
    """Use as Event """

