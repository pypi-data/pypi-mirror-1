### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: friendshipannotation.py 51716 2008-09-15 23:32:26Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51716 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IFriendshipAnnotation,IFriendshipAnnotationAble,friendshipannotationkey
from BTrees.IIBTree import IISet
from zope.app.zapi import getUtility
from friend import Friend
from zope.location.interfaces import ILocation
from zope.app.intid.interfaces import IIntIds

FS_ALREADY = 0
FS_FRIEND = 1
FS_SUGGEST = 2

class FriendshipAnnotation(Persistent) :
    __doc__ = IFriendshipAnnotation.__doc__
    implements(IFriendshipAnnotation,ILocation)

    __parent__ = None
    __name__ = ""
    
    def __init__(self,ob) :
        self.set = IISet()
        self.suggestset = IISet()
        self.__parent__ = ob
        self.__name__ = "++annotations++" + friendshipannotationkey

    def suggest(self,ob) :
        cid = getUtility(IIntIds,context=self).getId(self.__parent__)
        pid = getUtility(IIntIds,context=ob).getId(ob)
        
        if pid in self.suggestset :
            return FS_ALREADY  
        elif pid in self.set :
            if cid in IFriendshipAnnotation(ob).suggestset :
                IFriendshipAnnotation(ob).agree(pid)
            else :
                IFriendshipAnnotation(ob).add(self.__parent__)
            return FS_FRIEND
    
        IFriendshipAnnotation(ob).add(self.__parent__)
        self.suggestset.insert(pid)
        return FS_SUGGEST

    def agree(self,id) :
        if id in self.suggestset :
            self.suggestset.remove(id)
            self.set.insert(id)
        
    def reject(self,id) :
        try :
            self.suggestset.remove(id)
        except KeyError :
            pass
          
    def remove(self,id) :
        try :
            self.set.remove(id)
        except KeyError :
            pass            
        
    def add(self,ob) :
        if IFriendshipAnnotationAble.providedBy(ob) :        
            self.set.insert(getUtility(IIntIds,context=self).getId(ob))
        else :
            raise TypeError
            
    def friends(self) :
        intids = getUtility(IIntIds,context=self)
        for key in self.set :
            try :
                ob = intids.getObject(key)
            except KeyError :
                #self.set.remove(key)
                print "Invalid friend removed"
            else :
                yield Friend(key,ob,IFriendshipAnnotation(ob).check(self.__parent__))

    @property
    def friendslength(self) :
        return len(self.set)

    def suggests(self) :
        intids = getUtility(IIntIds,context=self)
        for key in list(self.suggestset) :
            try :
                ob = intids.getObject(key)
            except KeyError :
                self.suggestset.remove(key)
                print "Invalid friendship suggest removed"

            else :
                yield Friend(key,ob,False)                                
                            
    @property
    def suggestslength(self) :
        return len(self.suggestset)


    def check(self,ob) :
        return getUtility(IIntIds,context=ob).getId(ob) in self.set            

                                        