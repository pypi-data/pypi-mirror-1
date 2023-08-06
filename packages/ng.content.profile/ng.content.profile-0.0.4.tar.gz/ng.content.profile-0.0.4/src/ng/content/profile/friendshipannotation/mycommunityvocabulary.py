### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Vocabuary class to construct list of communities from list of friends

$Id: mycommunityvocabulary.py 52232 2008-12-27 22:57:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52232 $"

from ng.site.addon.profile.profileadapter.profileadapter import profileadaptersimple
from interfaces import IFriendshipAnnotation
from zope.component import providedBy
from ng.content.profile.communityobjectqueueannotation.interfaces import ICommunityObjectQueueAnnotationAble
from ng.content.article.interfaces import IDocShort
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

def mycommunityvocabulary(context) :
    try :
        profile = profileadaptersimple(context) 
    except KeyError :
        return SimpleVocabulary([])
    
    if profile is None :
        return SimpleVocabulary([])
        
    return SimpleVocabulary(
        [ SimpleTerm(title=IDocShort(friend.profile).title, value = friend.id) 
            for friend in IFriendshipAnnotation(profile).friends() 
            if friend.status 
                and ICommunityObjectQueueAnnotationAble in  providedBy(friend.profile)]
        )
    