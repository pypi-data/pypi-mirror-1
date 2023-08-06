### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.annotation.redirectannotation
package

$Id: interfaces.py 52470 2009-02-07 09:25:57Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52470 $"


from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, URI
from zope.app.container.interfaces import IContained, IContainer



class URIEmpty(URI) :
    def _validate(self,value) :
        if value not in ["",u""] or self.required :
            super(URIEmpty,self)._validate(value)                


class IRedirectAnnotationAble(Interface) :
    """ IRedirectAnnotationAble interface
    """
    
    pass


class IRedirectAnnotation(Interface) :
    """ IRedirectAnnotation interface that discribe redirect
    """
    redirect = URIEmpty(
        title = u'Redirect URL',
        description = u'URL needed to redirect to',
        default = '',
        required = False)

redirectannotationkey = u"redirectannotation.redirectannotation.RedirectAnnotation"
