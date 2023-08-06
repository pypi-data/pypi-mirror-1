### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FriendObjectQueueAnnotation class for the Zope 3 based package

$Id: friendobjectqueueannotation.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from ng.app.objectqueue.objectqueue import ObjectQueue
from interfaces import IFriendObjectQueueAnnotation
from zope.interface import implements

class FriendObjectQueueAnnotation(ObjectQueue) :
    __doc__ = IFriendObjectQueueAnnotation.__doc__
    implements(IFriendObjectQueueAnnotation)

    count = 0                                        
    
    def handleAdded(self,ob) :
        self.count += 1
        return super(FriendObjectQueueAnnotation,self).handleAdded(ob)
        