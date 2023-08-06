### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FriendList mixin for the Zope 3 based friend annotation package

$Id: friendlist.py 52232 2008-12-27 22:57:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52232 $"

from zope.interface import implements
from ng.content.profile.friendshipannotation.interfaces import IFriendshipAnnotation
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog 
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from ng.content.profile.friendshipannotation.friendshipannotation import FS_ALREADY, FS_FRIEND, FS_SUGGEST


class FriendList(object) :
    """ """
    page = ViewPageTemplateFile("friendlist.pt")
    
    def __init__(self,*kv,**kw) :
        super(FriendList,self).__init__(*kv,**kw)
        self.friends = IFriendshipAnnotation(self.context)
    
    def suggest(self,*kv, **kw) :
        count = { FS_ALREADY : 0, FS_FRIEND : 0, FS_SUGGEST :0 }

        for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( self.request.principal.id, self.request.principal.id ) 
                          ) :
            count[self.friends.suggest(profile)] += 1
            
        l = []          
        if count[FS_ALREADY] :
            l.append( "friendship has been suggested already (%u)" % count[FS_ALREADY] )
        if count[FS_FRIEND] :
            l.append( "friendship accepted (%u)" % count[FS_FRIEND] )
        if count[FS_SUGGEST] :
            l.append( "friendship suggested (%u)" % count[FS_SUGGEST] )
            
        return self.page(self,message = ",".join(l).capitalize() + '.', *kv, **kw)

    def agree(self,id,*kv, **kw) :
        self.friends.agree(int(id))
        return self.page(self,message=u'Friendship suggestion accepted', *kv, **kw)
        
    def reject(self,id,*kv, **kw) :
        self.friends.reject(int(id))
        return self.page(self,message=u'Friendship suggestion rejected', *kv, **kw)
        
    def remove(self,id,*kv, **kw) :
        self.friends.remove(int(id))
        return self.page(self,message=u'Friendship denied', *kv, **kw)
          
