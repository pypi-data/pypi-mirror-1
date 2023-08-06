### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Vocabuary class to construct list of communities from list of friends

$Id: mycommunityvocabulary.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from ng.site.content.profileadapter.profileadapter import profileadaptersimple
from interfaces import IFriendshipAnnotation
from zope.component import providedBy
from ng.content.annotation.communityobjectqueueannotation.interfaces import ICommunityObjectQueueAnnotationAble
from ng.content.article.interfaces import IDocShort
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

def mycommunityvocabulary(context) :
    print context
    try :
        profile = profileadaptersimple(context) 
    except KeyError :
        return SimpleVocabulary([])
    
    if profile is None :
        return SimpleVocabulary([])
        
    return SimpleVocabulary(
        [ SimpleTerm(title=IDocShort(friend.profile).title, value = friend.id) 
            for friend in IFriendshipAnnotation(profile).friends() 
            if friend.status 
                and ICommunityObjectQueueAnnotationAble in  providedBy(friend.profile)]
        )
    