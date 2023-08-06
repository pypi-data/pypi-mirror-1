### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Hierarchy Climbing adapters to adapt to IFriendshipAnnotation

$Id: friendshipadapter.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from ng.content.annotation.friendshipannotation.interfaces import IFriendshipAnnotation
from zope.app.container.contained import IContained

def FriendshipAdapter(context) :
    an = IFriendshipAnnotation(IContained(context).__parent__)
    return an
        
def Site2FriendshipAdapter(context) :
    raise LookupError
  
    