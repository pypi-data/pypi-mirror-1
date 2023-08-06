### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RedirectAnnotationAbleAdapter class for the Zope 3 based
ng.content.annotation.redirectannotation package

$Id: redirectannotationableadapter.py 52471 2009-02-07 20:56:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52471 $"


from zope.annotation.interfaces import IAnnotations 
from redirectannotation import RedirectAnnotation
from interfaces import redirectannotationkey
from zope.security.proxy import removeSecurityProxy
from zope.location.location import LocationProxy 


def RedirectAnnotationAbleAdapter(context) :
    annotations = IAnnotations(context)
    try :
        ea = annotations[redirectannotationkey]
    except KeyError :
        ea = annotations[redirectannotationkey] = RedirectAnnotation()
    return LocationProxy(removeSecurityProxy(ea), context, "++annotations++" +  redirectannotationkey)
