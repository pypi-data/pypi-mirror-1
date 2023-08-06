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
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary
from ng.app.objectqueue.interfaces import IObjectQueueData

class IFriendshipAnnotationAble(Interface) :
    pass

class IFriendshipAnnotation(Interface) :
    """ """
    set = Field()
    suggestset = Field()

    friendslength = Int()
    suggestslength = Int()
    
    def suggest(ob) :
        """ Suggest friendship """
        
    def agree(id) :
        """ Agree on friendship suggestion """
        
    def reject(id) :
        """ Reject friendship suggestion """
        
    def remove(id) :
        """ Remove friend """
        
    def add(ob) :
        """ Add object into friendlist """
            
    def friends() :
        """ Get friendlist with status """
                            
    def suggests() :
        """ Get suggestlist """

    def check(ob) :
        """ Check friend status """

    def remove(ob) :
        """ Remove friend from friendlist """

class IFriend(Interface) :

    profile = Field(title=u"Friend profile", readonly=True)
    
    status = Bool(title=u"Status of friend", readonly=True, default=False)

    id = Int(title=u"Object ID", readonly=True)


class IFriendlistAnnotation(IObjectQueueData) :
    """ """

class IFriendlistAnnotationAble(Interface) :
    """ """
    
    
friendshipannotationkey="friendshipannotation.friendshipannotation.FriendshipAnnotation"

friendlistannotationkey="friendlistannotation.friendlistannotation.FriendlistAnnotation"
