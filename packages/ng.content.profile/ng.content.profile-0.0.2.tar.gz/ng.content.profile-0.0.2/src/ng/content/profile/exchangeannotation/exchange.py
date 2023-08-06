### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Exchange class for the Zope 3 based ng.content.profile.excangeannotation package

$Id: exchange.py 51689 2008-09-11 20:59:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51689 $"

from persistent import Persistent
from zope.interface import Interface, implements
from interfaces import IExchangeContainer
from zope.app.container.ordered import OrderedContainer
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContained

class Exchange(OrderedContainer,Contained) :
    __doc__ = IExchangeContainer.__doc__
    implements(IExchangeContainer,IContained)
    __parent__ = None

    def __init__(self,*kv,**kw) :
        super(Exchange,self).__init__(*kv,**kw)
        
    def add(self,message) :
        try :
          num = int(self.keys()[-1])
        except (IndexError,TypeError,UnicodeEncodeError) :
          num = 1
        else :                    
          while "%06u" % num in self :
            num += 1
            
        title = "%06u" % num
          
        self[title] = message
        message.__name__ = title
        message.__parent__ = self
        return message
