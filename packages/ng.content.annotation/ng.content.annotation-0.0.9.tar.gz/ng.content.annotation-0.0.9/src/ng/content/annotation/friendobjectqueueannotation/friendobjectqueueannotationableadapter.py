### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: friendobjectqueueannotationableadapter.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from zope.annotation.interfaces import IAnnotations 
from ng.app.objectqueue.objectqueue import ObjectQueue

from interfaces import friendobjectqueueannotationkey

def IFriendObjectQueueAnnotationAbleAdapter(context) :


    try :
        an = IAnnotations(context)[friendobjectqueueannotationkey]
    except KeyError :
        an = IAnnotations(context)[friendobjectqueueannotationkey] = ObjectQueue(context)
    return an

