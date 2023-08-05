### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: dictannotation.py 49955 2008-02-06 20:26:35Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49955 $"

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
    