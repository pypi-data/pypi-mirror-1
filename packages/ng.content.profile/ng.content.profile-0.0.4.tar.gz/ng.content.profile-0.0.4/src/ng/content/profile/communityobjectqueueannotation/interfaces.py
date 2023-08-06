### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51784 2008-09-25 09:00:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51784 $"
 
from zope.interface import Interface
from zope.schema import TextLine, Choice, Tuple, Field, Bool, Int
from ng.app.objectqueue.interfaces import IObjectQueueData

class ICommunityObjectQueueAnnotation(IObjectQueueData) :
    """ """
    #count = Int(title=u"New object")

class ICommunityObjectQueueAnnotationAble(Interface) :
    """ """

class ICommunityObjectQueueAble(Interface) :
    """ """

communityobjectqueueannotationkey="commmunityobjectqueueannotation.commmunityobjectqueueannotation.CommunityObjectQueueAnnotation"
