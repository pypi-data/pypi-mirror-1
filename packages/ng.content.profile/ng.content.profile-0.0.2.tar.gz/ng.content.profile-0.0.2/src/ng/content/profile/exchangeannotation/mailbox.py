### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mailbox class for the Zope 3 based mailbox package

$Id: mailbox.py 51689 2008-09-11 20:59:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51689 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implementsOnly, implementedBy
from interfaces import IMailboxContainer, IExchangeAnnotation
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IContained
from zope.location.location import LocationProxy 
from zope.security.proxy import removeSecurityProxy



ifs = set(implementedBy(BTreeContainer))
ifs.remove(IContained)

class Mailbox(BTreeContainer) :
    __doc__ = IMailboxContainer.__doc__
    implementsOnly(IExchangeAnnotation,IMailboxContainer,*ifs)
    __parent__ = None



    def __init__(self,*kv,**kw) :
        super(Mailbox,self).__init__(*kv,**kw)
        
    def __nonzero__(self) :
        return True
        
    def __getitem__(self,name) :
        print "getitem"

        return LocationProxy(
             removeSecurityProxy(super(Mailbox,self).__getitem__(name)),
             self,
             name
		)
                
    def get(self,name,default=None) :
        print "GET",name
        try :
            return self[name] 
        except KeyError :
            return default   
            
    def values(self,name,default) :
        print "values"
        return [ self[x] for x in self.keys() ]                                

    def items(self) :
        print "items"
        return [ (x,self[x]) for x in self.keys() ]                                
        