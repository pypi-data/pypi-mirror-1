### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"
 
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

    wikiword = TextLine(title=u'Wiki', description=u"Word entered to link on wikipedia page", required=False)

dictannotationkey="dictannotation.dictannotation.DictAnnotation"

