### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ProductAnnotationAbleAdapter class for the Zope 3 based
ng.content.annotation.productannotation package

$Id: productannotationableadapter.py 52471 2009-02-07 20:56:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52471 $"


from zope.annotation.interfaces import IAnnotations 
from productannotation import ProductAnnotation
from interfaces import productannotationkey
from zope.location.location import LocationProxy 

def ProductAnnotationAbleAdapter(context) :
    annotations = IAnnotations(context)
    try :
        ea = annotations[productannotationkey]
    except KeyError :
        ea = annotations[productannotationkey] = ProductAnnotation()
    return LocationProxy(ea, context, "++annotations++" +  productannotationkey)
