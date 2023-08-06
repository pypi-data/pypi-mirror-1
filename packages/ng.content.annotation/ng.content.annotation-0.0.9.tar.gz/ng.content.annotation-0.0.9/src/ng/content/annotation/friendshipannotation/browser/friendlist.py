### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FriendList mixin for the Zope 3 based friend annotation package

$Id: friendlist.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from zope.interface import implements
from ng.content.annotation.friendshipannotation.interfaces import IFriendshipAnnotation
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog 
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class FriendList(object) :
    """ """
    page = ViewPageTemplateFile("friendlist.pt")
    
    def __init__(self,*kv,**kw) :
        super(FriendList,self).__init__(*kv,**kw)
        self.friends = IFriendshipAnnotation(self.context)
    
    def suggest(self,*kv, **kw) :
        count = 0
        for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( self.request.principal.id, self.request.principal.id ) 
                          ) :
            count+= 1
            IFriendshipAnnotation(profile).suggest(self.context)
        return self.page(self,message=u'Suggested %u friendship' % count, *kv, **kw)

    def agree(self,id,*kv, **kw) :
        self.friends.agree(int(id))
        return self.page(self,message=u'Friendship suggestion accepted', *kv, **kw)
        
    def reject(self,id,*kv, **kw) :
        self.friends.reject(int(id))
        return self.page(self,message=u'Friendship suggestion rejected', *kv, **kw)
        
    def remove(self,id,*kv, **kw) :
        self.friends.remove(int(id))
        return self.page(self,message=u'Friendship denied', *kv, **kw)
          
