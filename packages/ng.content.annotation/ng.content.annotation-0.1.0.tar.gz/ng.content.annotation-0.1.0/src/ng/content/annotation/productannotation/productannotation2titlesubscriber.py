### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The adapter ProductAnnotation2TitleSubscriber that adopt IAttributeAnnotatable
   interface to ITitle interface

$Id: productannotation2titlesubscriber.py 52274 2009-01-07 13:03:45Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52274 $"

from interfaces import IProductAnnotation
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase

class ProductAnnotation2TitleSubscriber( AnyTitleSubscriberBase ) :

    order = 2

    @property
    def title(self) :
        return IProductAnnotation(self.context).title

