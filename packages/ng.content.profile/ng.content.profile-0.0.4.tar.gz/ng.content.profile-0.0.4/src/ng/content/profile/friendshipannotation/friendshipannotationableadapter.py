### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: friendshipannotationableadapter.py 51646 2008-09-07 09:16:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51646 $"

from friendshipannotation import FriendshipAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import friendshipannotationkey
from zope.security.proxy import removeSecurityProxy

def IFriendshipAnnotationAbleAdapter(context) :
    context = removeSecurityProxy(context)


    try :
        an = IAnnotations(context)[friendshipannotationkey]
    except KeyError :
        an = IAnnotations(context)[friendshipannotationkey] = FriendshipAnnotation(context)

    return an
