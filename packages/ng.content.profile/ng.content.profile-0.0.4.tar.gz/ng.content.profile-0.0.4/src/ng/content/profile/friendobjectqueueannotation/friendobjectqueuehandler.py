### -*- coding: utf-8 -*- #############################################
#######################################################################
"""handleAdded, handleModified and handleRemoved scripts for the Zope 3
based friendobjectqueue package

$Id: friendobjectqueuehandler.py 52232 2008-12-27 22:57:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52232 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from ng.app.objectqueue.interfaces import IObjectQueueHandle
from interfaces import IFriendObjectQueueAnnotation
from ng.content.profile.friendshipannotation.interfaces import IFriendshipAnnotation
from zope.security.proxy import removeSecurityProxy

def handleAdded(ob, event) :
    try :
        friendship = IFriendshipAnnotation(ob)
    except LookupError :
        pass
    else:         
        for queue in [ IFriendObjectQueueAnnotation(friend.profile,None) for friend in friendship.friends() if friend.status ] :
            if queue is not None :
                IObjectQueueHandle(queue).handleAdded(ob)

def handleModified(ob, event) :
    try :
        friendship = IFriendshipAnnotation(ob)
    except LookupError :
        pass
    else :
        for queue in [ IFriendObjectQueueAnnotation(friend.profile,None) for friend in friendship.friends() if friend.status ] :
            if queue is not None :
                IObjectQueueHandle(queue).handleModified(ob)

def handleRemoved(ob, event) :
    try :
        friendship = IFriendshipAnnotation(ob)
    except LookupError :
        pass
    else :        
        for queue in [ IFriendObjectQueueAnnotation(friend.profile,None) for friend in friendship.friends() if friend.status ] :
            if queue is not None :
                IObjectQueueHandle(queue).handleRemoved(ob)
