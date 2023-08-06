### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The adapter ProfileAnnotation2TitleSubscriber that adopt IAttributeAnnotatable
   interface to ITitle interface

$Id: profileannotation2titlesubscriber.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from interfaces import IProfileAnnotation
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase

class ProfileAnnotation2TitleSubscriber( AnyTitleSubscriberBase ) :

    order = 2

    @property
    def title(self) :
        return " ".join(IProfileAnnotation(self.context).nickname)
