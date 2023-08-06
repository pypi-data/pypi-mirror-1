
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: docshortannotationableadapter.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "DocShort Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from docshortannotation import DocShortAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames
from zope.location.location import LocationProxy 
from zope.security.proxy import removeSecurityProxy
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.container.contained import ObjectAddedEvent
from zope.event import notify
from interfaces import docshortannotationkey
from transaction import get

def IDocShortAnnotationAbleAdapter(context) :

    try :
        an = LocationProxy(
		removeSecurityProxy(IAnnotations(context)[docshortannotationkey]),
		context,
		"++annotations++" + docshortannotationkey
		)
        notify(ObjectAddedEvent(an,context,"++annotations++" + docshortannotationkey))
        print "Activate DSA",an
    except KeyError :
    	dsa = IAnnotations(context)[docshortannotationkey] = DocShortAnnotation()
        an = LocationProxy(  removeSecurityProxy(dsa), context, "++annotations++" + docshortannotationkey )
        #notify(ObjectCreatedEvent(an))
        get().commit()
        notify(ObjectAddedEvent(an,context,"++annotations++" + docshortannotationkey))
        print "Create DSA",an

    return an
