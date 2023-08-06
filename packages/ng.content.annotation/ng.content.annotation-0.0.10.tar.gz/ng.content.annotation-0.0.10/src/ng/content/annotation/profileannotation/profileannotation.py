### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: profileannotation.py 51919 2008-10-21 19:01:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51919 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IProfileAnnotation,IProfileAnnotationAble,IProfileAnnotationSystem,profileannotationkey
from zope.location.interfaces import ILocation
import datetime

class ProfileAnnotation(Persistent) :
    __doc__ = IProfileAnnotation.__doc__
    implements(IProfileAnnotation,IProfileAnnotationSystem,ILocation)
    __parent__=None
    __name__= "++annotations++" + profileannotationkey

    userid = ""
    nickname = u""
    email = u""
    sex = u""
    city = u""
    birthday = None
    interests = set([])
    
    @property
    def age(self) :
      age = datetime.datetime.now().year - self.birthday.year
      if datetime.datetime.now().month >= self.birthday.month \
        and datetime.datetime.now().day >= self.birthday.day :
          return age
      return age - 1
          