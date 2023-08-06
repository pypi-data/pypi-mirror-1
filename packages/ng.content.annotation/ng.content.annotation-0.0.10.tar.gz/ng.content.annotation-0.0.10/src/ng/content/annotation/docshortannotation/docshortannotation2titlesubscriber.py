### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: docshortannotation2titlesubscriber.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from zope.component import adapts
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase
from ng.content.annotation.docshortannotation.interfaces import IDocShortAnnotationAble
from ng.content.article.interfaces import IDocShort

class DocShortAnnotation2TitleSubscriber(AnyTitleSubscriberBase) :

    adapts(IDocShortAnnotationAble)
    order = 4
        
    @property
    def title(self) :
        return IDocShort(self.context).title or u""
