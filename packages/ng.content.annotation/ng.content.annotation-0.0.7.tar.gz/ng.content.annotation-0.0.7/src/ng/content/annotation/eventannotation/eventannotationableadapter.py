### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EventAnnotationAbleAdapter class for the Zope 3 based eventannotation package

$Id: eventannotationableadapter.py 49955 2008-02-06 20:26:35Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49955 $"


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
