### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: dictannotation.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IDictAnnotation,IDictAnnotationAble

class DictAnnotation(Persistent) :
    __doc__ = IDictAnnotation.__doc__
    implements(IDictAnnotation)

    # See dictannotation.interfaces.IDictAnnotation
    suffixes = ''
    keyword = []
    area = []
    gender = []
    wikiword=''    