### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Comment class for the Zope 3 based comment annotation package

$Id: message.py 51883 2008-10-20 19:14:59Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51883 $"

from zope.interface import implements
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContained
from interfaces import IMessage,IExchangeContained
import datetime
import pytz

class Message(Contained,Persistent) :
    implements(IMessage, IExchangeContained, IContained)


    def __init__(self,*kv,**kw) :
        super(Message,self).__init__(*kv,**kw)
        self.created = datetime.datetime.now()#pytz.utc)        

    title = u""
    abstract = u""
    created = datetime.datetime.now() #pytz.utc)
    author = u""



