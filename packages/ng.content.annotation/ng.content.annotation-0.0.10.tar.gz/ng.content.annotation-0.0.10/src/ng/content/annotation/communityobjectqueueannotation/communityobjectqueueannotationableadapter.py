### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: communityobjectqueueannotationableadapter.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from zope.annotation.interfaces import IAnnotations 
from ng.app.objectqueue.objectqueue import ObjectQueue
from interfaces import communityobjectqueueannotationkey

def ICommunityObjectQueueAnnotationAbleAdapter(context) :
    try :
        an = IAnnotations(context)[communityobjectqueueannotationkey]
    except KeyError :
        an = IAnnotations(context)[communityobjectqueueannotationkey] = ObjectQueue(context)
        an.__parent__ = context
    return an

