### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ProductAnnotationAbleAdapter class for the Zope 3 based
ng.content.annotation.productannotation package

$Id: productannotationableadapter.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"


from zope.annotation.interfaces import IAnnotations 
from productannotation import ProductAnnotation
from interfaces import productannotationkey


def ProductAnnotationAbleAdapter(context) :
    annotations = IAnnotations(context)
    try :
        ea = annotations[productannotationkey]
    except KeyError :
        ea = annotations[productannotationkey] = ProductAnnotation()
    return ea
