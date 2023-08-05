### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: dictannotationableadapter.py 49001 2007-12-24 13:29:26Z antel $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49001 $"

from dictannotation import DictAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import dictannotationkey

def IDictAnnotationAbleAdapter(context) :

    try :
        an = IAnnotations(context)[dictannotationkey]
    except KeyError :
        an = IAnnotations(context)[dictannotationkey] = DictAnnotation()
    return an
