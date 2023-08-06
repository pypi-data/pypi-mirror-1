### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Comment class for the Zope 3 based comment annotation package

$Id: messageadd.py 51689 2008-09-11 20:59:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51689 $"

from zope.interface import implements
from ng.content.profile.exchangeannotation.interfaces import IMessage
from ng.content.profile.exchangeannotation.message import Message

from zope.app.zapi import getUtility
from zope.schema import getFieldNames


class MessageAdd(object) :

    def getData(self,*kv,**kw) :
        return [ (x,IMessage[x].default) for x in getFieldNames(IMessage)]

    def setData(self,d,**kw) :
        message = Message()
        self.context.add(message)
        for x in getFieldNames(IMessage) :
            setattr(message,x,d[x])
        return True

