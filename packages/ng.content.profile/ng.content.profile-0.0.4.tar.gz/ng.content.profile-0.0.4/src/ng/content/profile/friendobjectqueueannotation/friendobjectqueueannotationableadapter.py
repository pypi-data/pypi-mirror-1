### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: friendobjectqueueannotationableadapter.py 51784 2008-09-25 09:00:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51784 $"

from zope.annotation.interfaces import IAnnotations 
from friendobjectqueueannotation import FriendObjectQueueAnnotation
from interfaces import friendobjectqueueannotationkey

def IFriendObjectQueueAnnotationAbleAdapter(context) :
    try :
        an = IAnnotations(context)[friendobjectqueueannotationkey]
    except KeyError :
        an = IAnnotations(context)[friendobjectqueueannotationkey] = FriendObjectQueueAnnotation(context)
        an.__parent__ = context
    return an

