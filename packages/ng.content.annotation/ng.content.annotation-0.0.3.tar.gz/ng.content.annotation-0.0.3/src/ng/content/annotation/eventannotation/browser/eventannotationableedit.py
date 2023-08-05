### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EventAnnotationAbleEdit class for the Zope 3 based eventannotation package

$Id: eventannotationableedit.py 49040 2007-12-27 05:18:27Z corbeau $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49040 $"

from zope.schema import getFieldNames
from eventannotation.interfaces import IEventAnnotation

class EventAnnotationAbleEdit(object) :

    def getData(self, *kv, **kw) :
        self.ea = IEventAnnotation(self.context)
        return [(x, getattr(self.ea, x)) for x in  getFieldNames(IEventAnnotation)]

    def setData(self, d, **kw) :
        for x in getFieldNames(IEventAnnotation) :
            setattr(self.ea, x, d[x])
        return True
