### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: profileannotationableadapter.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from profileannotation import ProfileAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import profileannotationkey

def IProfileAnnotationAbleAdapter(context) :

    try :
        an = IAnnotations(context)[profileannotationkey]
    except KeyError :
        an = IAnnotations(context)[profileannotationkey] = ProfileAnnotation()
        an.__parent__ = context
    return an
