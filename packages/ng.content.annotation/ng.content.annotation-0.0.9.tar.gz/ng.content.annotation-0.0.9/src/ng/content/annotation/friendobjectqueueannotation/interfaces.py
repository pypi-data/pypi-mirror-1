### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"
 
from zope.interface import Interface
from zope.schema import TextLine, Choice, Tuple, Field, Bool, Int
from ng.app.objectqueue.interfaces import IObjectQueueData


class IFriendObjectQueueAnnotation(IObjectQueueData) :
    """ """

class IFriendObjectQueueAnnotationAble(Interface) :
    """ """

class IFriendObjectQueueAble(Interface) :
    """ """

    
friendobjectqueueannotationkey="friendobjectqueueannotation.friendobjectqueueannotation.FriendobjectqueueAnnotation"
