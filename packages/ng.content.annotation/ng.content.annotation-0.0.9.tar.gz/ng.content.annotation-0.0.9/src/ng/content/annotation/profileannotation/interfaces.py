### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Choice, Tuple, Int, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary


class IProfileAnnotationAble(Interface) :
    pass


class IProfileAnnotationSystem(Interface) :
    userid = TextLine(title=u"User Id",
                    description=u"User Id in Authentication System",
                    required=True
                    )

class IProfileAnnotationOwner(Interface) :
    """ """


    nickname = TextLine(title=u'Nickname',
                    description=u'Your nickname',
                    required=True,
                    default=u'',
                   )

    email = TextLine(title=u'E-Mail',
                    description=u'Your E-Mail addresss',
                    required=False,
                    default=u'',
                   )

    sex = Choice(title=u'Sex',
                  vocabulary = SimpleVocabulary.fromValues([u'Male','Not Entered',u'Female',u'EveryDay']),
                  required=False,
                  )


    city = TextLine(title=u'City',
                    description=u'Your city',
                    required=False,
                    default=u'',
                   )

    birthday = Datetime(title=u'Birthday',
                    description=u'Your Birth Day',
                    required=False,
                    default=None,
                   )

    interests = Choice(title=u'Interests',
                  description=u'Your interest areas',
                  vocabulary = SimpleVocabulary.fromValues([u"Zope", u"NeuralNetwork", u"Programming", u"Other"]),
                  required=False
                  )

    age = Int(title=u'Age',readonly=True,default=0)

class IProfileAnnotationForm(IProfileAnnotationOwner) :
    """ """

class IProfileAnnotation(IProfileAnnotationForm) :
    """ """

profileannotationkey="profileannotation.profileannotation.ProfileAnnotation"
