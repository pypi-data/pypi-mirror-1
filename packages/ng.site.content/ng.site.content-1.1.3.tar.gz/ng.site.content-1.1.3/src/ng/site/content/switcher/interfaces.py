### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Dwitchable markers

$Id: interfaces.py 51965 2008-10-23 21:55:22Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51965 $"
__date__ = "$Date: 2008-10-24 01:55:22 +0400 (Птн, 24 Окт 2008) $"
 
from ng.content.article.interfaces import IDocFormatSwitcher, IArticleDesignSwitcher
from zope.interface import Interface

class IArticleDivided(IArticleDesignSwitcher) :
    "Divided Design"
    pass

class IArticlePage(IArticleDesignSwitcher):
    "Page Design"
    pass

class IArticleREST(IDocFormatSwitcher) :
    "Restructured text data"
    pass

class IArticleST(IDocFormatSwitcher):
    "Structured text data"
    pass

class IArticleASIS(IDocFormatSwitcher):
    "Preformated Text"
    pass

class IArticleHTML(IDocFormatSwitcher):
    "HTML text data"
    pass


class IDivisionDesignSwitcher(Interface):
    "Default Design"
    pass

class IDivisionDictionarySwitcher(IDivisionDesignSwitcher) :
    "Dictionary design "

class IDivisionItemSwitcher(IDivisionDesignSwitcher) :
    "Item design "
    
    
