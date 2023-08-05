### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49610 2008-01-21 12:48:34Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49610 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Choice, Tuple
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary

class IDictAnnotationAble(Interface) :
    pass

class IDictAnnotation(Interface) :
    """ """
    keyword = Tuple(title=u'keywords',
                    description=u'Some keywords',
                    required=False,
                    default=(),
                    value_type=TextLine(title=u'keyword'),
                   )
                
    gender = Choice(title=u'gender',
                  vocabulary = SimpleVocabulary.fromValues(['F','M'])
                  )

    suffixes = TextLine(title=u'suffixes')

    area = Choice(title=u'Area',
                  vocabulary = SimpleVocabulary.fromValues([1, 2, 3])
                  )

dictannotationkey="dictannotation.dictannotation.DictAnnotation"

