### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The adapter DictAnnotation2TitleSubscriber that adopt IAttributeAnnotatable
   interface to ITitle interface

$Id: dictannotation2titlesubscriber.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__credits__  = "Yegor Shershnev"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from interfaces import IDictAnnotation
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase

class DictAnnotation2TitleSubscriber( AnyTitleSubscriberBase ) :

    order = 2

    @property
    def title(self) :
        return " ".join(IDictAnnotation(self.context).keyword)
