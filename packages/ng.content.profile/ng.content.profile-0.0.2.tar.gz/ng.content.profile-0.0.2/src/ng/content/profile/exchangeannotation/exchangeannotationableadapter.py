### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: exchangeannotationableadapter.py 51689 2008-09-11 20:59:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51689 $"

from mailbox import Mailbox
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames
from zope.location.location import LocationProxy 
from zope.security.proxy import removeSecurityProxy
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.container.contained import ObjectAddedEvent
from zope.event import notify
from interfaces import exchangeannotationkey
from transaction import get

def IExchangeAnnotationAbleAdapter(context) :
    try :
        an = LocationProxy(
             removeSecurityProxy(IAnnotations(context)[exchangeannotationkey]),
             context,
             "++annotations++" + exchangeannotationkey
		)
        print "Activate Mailbox",an
    except KeyError :
    	IAnnotations(context)[exchangeannotationkey] = Mailbox()
    	dsa = IAnnotations(context)[exchangeannotationkey]
        an = LocationProxy(  removeSecurityProxy(dsa), context, "++annotations++" + exchangeannotationkey )
        notify(ObjectCreatedEvent(an))
        get().commit()
        #notify(ObjectAddedEvent(an,context,"++annotations++" + exchangeannotationkey))
        notify(ObjectAddedEvent(dsa,context,"++annotations++" + exchangeannotationkey))
        print "Create Mailbox",an

    return an
