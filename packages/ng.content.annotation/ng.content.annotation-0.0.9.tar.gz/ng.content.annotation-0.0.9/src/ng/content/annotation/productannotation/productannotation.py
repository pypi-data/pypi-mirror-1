### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ProductAnnotation class for the Zope 3 based
ng.content.annotation.productannotation package

$Id: productannotation.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IProductAnnotation
from persistent import Persistent

class ProductAnnotation(Persistent) :
    """ ProductAnnotation class
    """
    implements(IProductAnnotation)

    title = ""
    
    ispypi = False
    
    repository = ""
    
    archive = ""
    