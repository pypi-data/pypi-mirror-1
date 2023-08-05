### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49878 2008-02-02 14:28:40Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49878 $"
 
from ng.content.annotation.annotationswitcher.interfaces import IAnnotationSwitcher
from ng.content.annotation.dictannotation.interfaces import IDictAnnotationAble
from ng.content.annotation.eventannotation.interfaces import IEventAnnotationAble

class IAnnotationSwitcherDict(IAnnotationSwitcher,IDictAnnotationAble) :
    """Use as dictionary """

class IAnnotationSwitcherEvent(IAnnotationSwitcher,IEventAnnotationAble) :
    """Use as Event """

