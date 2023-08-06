### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The adapter ProfileAnnotation2TitleSubscriber that adopt IAttributeAnnotatable
   interface to ITitle interface

$Id: profileannotation2titlesubscriber.py 51256 2008-07-06 16:03:35Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51256 $"

from interfaces import IProfileAnnotation
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase

class ProfileAnnotation2TitleSubscriber( AnyTitleSubscriberBase ) :

    order = 2

    @property
    def title(self) :
        return " ".join(IProfileAnnotation(self.context).nickname)
