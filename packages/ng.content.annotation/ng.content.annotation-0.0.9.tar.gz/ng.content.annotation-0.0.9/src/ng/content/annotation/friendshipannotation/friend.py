### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Friend class for the Zope 3 based friend annotation package

$Id: friend.py 51563 2008-08-31 09:41:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51563 $"

from zope.interface import implements
from interfaces import IFriend

class Friend(object) :
    implements(IFriend)
    profile = None
    status = False

    def __init__(self,id,profile,status) :
        self.id = id
        self.profile = profile
        self.status = status
        