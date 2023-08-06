### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Friend class for the Zope 3 based friend annotation package

$Id: friend.py 51318 2008-07-09 12:01:46Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51318 $"

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
        