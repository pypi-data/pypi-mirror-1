### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51304 2008-07-08 15:31:57Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51304 $"
 
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

