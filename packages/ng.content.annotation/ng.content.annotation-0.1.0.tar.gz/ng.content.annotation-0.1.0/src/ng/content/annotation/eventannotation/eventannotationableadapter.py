### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EventAnnotationAbleAdapter class for the Zope 3 based
ng.content.annotation.eventannotation package

$Id: eventannotationableadapter.py 52471 2009-02-07 20:56:31Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52471 $"


from zope.annotation.interfaces import IAnnotations 
from eventannotation import EventAnnotation
from interfaces import eventannotationkey
from zope.location.location import LocationProxy 


def EventAnnotationAbleAdapter(context) :
    annotations = IAnnotations(context)
    try :
        ea = annotations[eventannotationkey]
    except KeyError :
        ea = annotations[eventannotationkey] = EventAnnotation()
    return LocationProxy(ea, context, "++annotations++" + eventannotationkey)
