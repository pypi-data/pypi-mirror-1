### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Choice, Tuple
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary


class IDocShortAnnotationAble(Interface) :
    pass

docshortannotationkey="ng.content.annotation.docshortannotation.DocShortAnnotation"

