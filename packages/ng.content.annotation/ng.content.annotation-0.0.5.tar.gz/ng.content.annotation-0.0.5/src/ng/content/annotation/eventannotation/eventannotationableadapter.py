### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EventAnnotationAbleAdapter class for the Zope 3 based eventannotation package

$Id: eventannotationableadapter.py 49625 2008-01-21 15:22:18Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49625 $"


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
