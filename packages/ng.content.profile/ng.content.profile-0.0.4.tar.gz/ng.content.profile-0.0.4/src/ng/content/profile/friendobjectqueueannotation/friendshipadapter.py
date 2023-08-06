### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Hierarchy Climbing adapters to adapt to IFriendshipAnnotation

$Id: friendshipadapter.py 52232 2008-12-27 22:57:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52232 $"

from ng.content.profile.friendshipannotation.interfaces import IFriendshipAnnotation
from zope.app.container.contained import IContained

def FriendshipAdapter(context) :
    an = IFriendshipAnnotation(IContained(context).__parent__)
    return an
        
def Site2FriendshipAdapter(context) :
    raise LookupError
  
    