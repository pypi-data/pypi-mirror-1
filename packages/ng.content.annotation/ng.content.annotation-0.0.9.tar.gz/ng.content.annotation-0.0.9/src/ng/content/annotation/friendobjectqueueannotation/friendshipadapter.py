### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Hierarchy Climbing adapters to adapt to IFriendshipAnnotation

$Id: friendshipadapter.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from ng.content.annotation.friendshipannotation.interfaces import IFriendshipAnnotation
from zope.app.container.contained import IContained

def FriendshipAdapter(context) :
    print "friendship adapter",context
    an = IFriendshipAnnotation(IContained(context).__parent__)
    print "return", an
    return an
        
def Site2FriendshipAdapter(context) :
    print "friendship site",context
    raise LookupError
  
    