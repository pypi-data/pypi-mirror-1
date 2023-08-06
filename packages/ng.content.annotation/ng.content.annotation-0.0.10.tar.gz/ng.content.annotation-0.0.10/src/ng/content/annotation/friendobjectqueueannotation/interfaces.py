### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"
 
from zope.interface import Interface
from zope.schema import TextLine, Choice, Tuple, Field, Bool, Int
from ng.app.objectqueue.interfaces import IObjectQueueData

class IFriendObjectQueueAnnotation(IObjectQueueData) :
    """ """
    count = Int(title=u"New object")

class IFriendObjectQueueAnnotationAble(Interface) :
    """ """

class IFriendObjectQueueAble(Interface) :
    """ """

    
friendobjectqueueannotationkey="friendobjectqueueannotation.friendobjectqueueannotation.FriendobjectqueueAnnotation"
