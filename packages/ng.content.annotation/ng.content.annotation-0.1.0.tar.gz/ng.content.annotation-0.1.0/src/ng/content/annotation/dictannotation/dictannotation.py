### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: dictannotation.py 50941 2008-04-05 11:45:06Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50941 $"

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