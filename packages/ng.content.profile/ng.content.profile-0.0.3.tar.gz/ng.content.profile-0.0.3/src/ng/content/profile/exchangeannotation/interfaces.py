### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51883 2008-10-20 19:14:59Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51883 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Choice, Tuple, Field, Int
from zope.app.container.interfaces import IContained, IContainer, IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.content.article.interfaces import IDocAbstract

class ICommonContainer(Interface) :
    pass

class IExchangeAnnotationAble(Interface) :
    pass

class IMailboxContent(Interface):
    """ Interface for article content """

class IMailboxData(Interface):
    """ Interface for mailbox data """
    count = Int(title=u"Message number",default=0,min=0)

class IMailboxContained(IContained,IMailboxContent) :
    """ Mailbox Contained """

    __parent__ = Field(
        constraint = ContainerTypesConstraint(ICommonContainer))


class IMailboxContainer(IContainer,ICommonContainer) :
    """ Article Container """

    def __setitem__(name, object) :
        """ Add IArticle Content """

    __setitem__.precondition = ItemTypePrecondition(IMailboxContent)

class IExchangeAnnotation(IMailboxData) :
    pass


class IExchangeContent(Interface) :
    """ Interface for article content """

class IExchangeContained(IContained,IExchangeContent) :
    """ Article Contained """
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ICommonContainer))


class IExchangeData(Interface) :
    count = Int(title=u"Message number",default=0,min=0)


class IExchangeContainer(IOrderedContainer,ICommonContainer,IMailboxContained,IExchangeData) :
    """ Article Container """

    def __setitem__(name, object) :
        """ Add exchanger content by name """

    __setitem__.precondition = ItemTypePrecondition(IExchangeContent)


class IMessage(IDocAbstract,IExchangeContained) :
    """ Commentary interface """


exchangeannotationkey="ng.content.profile.exchangeannotation.ExchangeAnnotation"

