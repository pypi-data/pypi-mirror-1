### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49878 2008-02-02 14:28:40Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49878 $"
 
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
                  vocabulary = SimpleVocabulary.fromValues([u'Male','Middle',u'Female']),
                  required=False,
                  )

    suffixes = TextLine(title=u'suffixes',required=False)

    area = Choice(title=u'Area',
                  vocabulary = SimpleVocabulary.fromValues([u"Zope", u"NeuralNetwork", u"Programming", u"Other"]),
                  required=False
                  )

dictannotationkey="dictannotation.dictannotation.DictAnnotation"

