### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: docshortannotation.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IDocShortAnnotationAble
from ng.content.article.interfaces import IDocShort
import datetime
import pytz

class DocShortAnnotation(Persistent) :
    __doc__ = IDocShort.__doc__
    implements(IDocShort)
    __parent__ = None

    def __init__(self,*kv,**kw) :
        self.created = datetime.datetime.now(pytz.utc)        
        
    title = u""
    abstract = u""
    created = datetime.datetime.now(pytz.utc)        
    author = u""
    iscontent = False
    isdivision = False
    ishidden = False
