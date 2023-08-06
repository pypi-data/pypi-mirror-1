### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Tuple, Choice
from ng.schema.interfaceswitcher.interfacesetfield import InterfaceSet
from ng.schema.interfaceswitcher.interfacechoicefield import InterfaceChoice

class IAnnotationSwitcher(Interface) :
    iface = InterfaceSet(
        title=u"Interface list",
        default = set([]),
        missing_value = set([])
        )

IAnnotationSwitcher['iface'].iface = IAnnotationSwitcher
    

    