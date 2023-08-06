### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51689 2008-09-11 20:59:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51689 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Choice, Tuple, Field
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

class IMailboxContained(IContained,IMailboxContent) :
    """ Article Contained """
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ICommonContainer))


class IMailboxContainer(IContainer,ICommonContainer) :
    """ Article Container """

    def __setitem__(name, object) :
        """ Add IArticle Content """

    __setitem__.precondition = ItemTypePrecondition(IMailboxContent)

class IExchangeAnnotation(Interface) :
    pass


class IExchangeContent(Interface) :
    """ Interface for article content """

class IExchangeContained(IContained,IExchangeContent) :
    """ Article Contained """
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ICommonContainer))


class IExchangeData(Interface) :
    pass

class IExchangeContainer(IOrderedContainer,ICommonContainer,IMailboxContained,IExchangeData) :
    """ Article Container """

    def __setitem__(name, object) :
        """ Add exchanger content by name """

    __setitem__.precondition = ItemTypePrecondition(IExchangeContent)


class IMessage(IDocAbstract,IExchangeContained) :
    """ Commentary interface """


exchangeannotationkey="ng.content.profile.exchangeannotation.ExchangeAnnotation"

