### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: convertable2titlesubscriber.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"

from zope.component import adapts
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase
from ng.app.converter.object2psadapter.interfaces import IAttributeConvertable, IPropertySheet

class Convertable2TitleSubscriber(AnyTitleSubscriberBase) :
    adapts(IAttributeConvertable)
    order = 3
            
    @property
    def title(self) :
        return IPropertySheet(self.context).get('title',u"")
