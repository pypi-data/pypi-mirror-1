### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RedirectAnnotation class for the Zope 3 based
ng.content.annotation.redirectannotation package

$Id: redirectannotation.py 52470 2009-02-07 09:25:57Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52470 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IRedirectAnnotation
from persistent import Persistent

class RedirectAnnotation(Persistent) :
    """ RedirectAnnotation class
    """
    implements(IRedirectAnnotation)

    redirect = ""
    
    