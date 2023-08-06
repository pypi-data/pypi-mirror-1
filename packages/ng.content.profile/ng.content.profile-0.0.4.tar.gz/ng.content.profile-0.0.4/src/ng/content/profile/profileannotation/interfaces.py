### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 52179 2008-12-25 11:14:10Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52179 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Choice, Tuple, Int, Datetime, Date, Set
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary
from ng.app.rubricator.tag.tagvocabulary.tagvocabulary import TagVocabulary


class IProfileAnnotationAble(Interface) :
    pass


class IProfileAnnotationSystem(Interface) :
    userid = TextLine(title=u"User Id",
                    description=u"User Id in Authentication System",
                    required=True
                    )

    password = TextLine(title=u"Password",
                    description=u"User Password in authentication system",
                    required=True
                    )

class IProfileAnnotationOwner(Interface) :
    """ """


    nickname = TextLine(title=u'Nickname',
                    description=u'Your nickname',
                    required=True,
                    default=u'',
                   )

    email = TextLine(title=u'E-Mail',
                    description=u'Your E-Mail addresss',
                    required=False,
                    default=u'',
                   )

    sex = Choice(title=u'Sex',
                  vocabulary = SimpleVocabulary.fromValues([u'Male',u'Female']),
                  required=False,
                  )


    city = TextLine(title=u'City',
                    description=u'Your city',
                    required=False,
                    default=u'',
                   )

    birthday = Date(title=u'Birthday',
                    description=u'Your Birth Day',
                    required=False,
                    default=None,
                   )

    interests = Set(title=u'Interests',
                  description=u'Your interest areas',
                  value_type = Choice(source = TagVocabulary()),
                  required=False,
                  )

    age = Int(title=u'Age',readonly=True,default=0)

class IProfileAnnotationForm(IProfileAnnotationOwner) :
    """ """

class IProfileAnnotation(IProfileAnnotationOwner,IProfileAnnotationSystem) :
    """ """

profileannotationkey="profileannotation.profileannotation.ProfileAnnotation"
    