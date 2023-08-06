### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: doctitle2titlesubscriber.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"

from zope.component import adapts
from ng.content.article.interfaces import IDocTitle
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase

class DocTitle2TitleSubscriber(AnyTitleSubscriberBase) :

    adapts(IDocTitle)
    order = 4
        
    @property
    def title(self) :
        return IDocTitle(self.context).title or u""
