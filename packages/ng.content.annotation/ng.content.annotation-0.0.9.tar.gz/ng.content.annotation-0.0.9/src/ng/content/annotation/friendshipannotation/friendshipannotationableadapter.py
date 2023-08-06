### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: friendshipannotationableadapter.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from friendshipannotation import FriendshipAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import friendshipannotationkey
from zope.security.proxy import removeSecurityProxy

def IFriendshipAnnotationAbleAdapter(context) :
    context = removeSecurityProxy(context)

    print 1, context

    try :
        print 2
        an = IAnnotations(context)[friendshipannotationkey]
    except KeyError :
        print 3
        an = IAnnotations(context)[friendshipannotationkey] = FriendshipAnnotation(context)

    return an
