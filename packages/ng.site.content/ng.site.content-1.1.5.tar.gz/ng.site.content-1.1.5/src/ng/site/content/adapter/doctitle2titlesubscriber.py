### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: doctitle2titlesubscriber.py 50628 2008-02-12 20:09:10Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50628 $"

from zope.component import adapts
from ng.content.article.interfaces import IDocTitle
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase

class DocTitle2TitleSubscriber(AnyTitleSubscriberBase) :

    adapts(IDocTitle)
    order = 4
        
    @property
    def title(self) :
        return IDocTitle(self.context).title or u""
