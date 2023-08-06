### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.annotation.productannotation
package

$Id: interfaces.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"


from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, URI
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint




class URIEmpty(URI) :
    def _validate(self,value) :
        if value not in ["",u""] or self.required :
            super(URIEmpty,self)._validate(value)                


class IProductAnnotationAble(Interface) :
    """ IProductAnnotationAble interface
    """
    
    pass


class IProductAnnotation(Interface) :
    """ IProductAnnotation interface that discribe product
    """
    title = TextLine(
        title = u"Name Of Product",
        description = u"Name Of Product",
        )

    ispypi = Bool(
        title = u"Product save in PYPI",
        description = u"Product save in PYPI",
        default=False,
        )
        
    repository = URIEmpty(
        title = u'Repository',
        description = u'Repository of product',
        default = '',
        required = False)

    archive = URIEmpty(
        title = u'Archive',
        description = u'Package archive of product',
        default = '',
        required = False)

productannotationkey = u"productannotation.productannotation.ProductAnnotation"
