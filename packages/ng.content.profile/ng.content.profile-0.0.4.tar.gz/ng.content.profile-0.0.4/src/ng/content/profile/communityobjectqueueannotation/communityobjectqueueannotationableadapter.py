### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: communityobjectqueueannotationableadapter.py 51784 2008-09-25 09:00:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51784 $"

from zope.annotation.interfaces import IAnnotations 
from ng.app.objectqueue.objectqueue import ObjectQueue
from interfaces import communityobjectqueueannotationkey

def ICommunityObjectQueueAnnotationAbleAdapter(context) :
    try :
        an = IAnnotations(context)[communityobjectqueueannotationkey]
    except KeyError :
        an = IAnnotations(context)[communityobjectqueueannotationkey] = ObjectQueue(context)
        an.__parent__ = context
    return an

