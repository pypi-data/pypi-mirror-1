### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EventAnnotationAbleAdapter class for the Zope 3 based
ng.content.annotation.eventannotation package

$Id: eventannotationableadapter.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"


from zope.annotation.interfaces import IAnnotations 
from eventannotation import EventAnnotation
from interfaces import eventannotationkey


def EventAnnotationAbleAdapter(context) :
    annotations = IAnnotations(context)
    try :
        ea = annotations[eventannotationkey]
    except KeyError :
        ea = annotations[eventannotationkey] = EventAnnotation()
    return ea
