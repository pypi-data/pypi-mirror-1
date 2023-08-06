### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Dwitchable markers

$Id: interfaces.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"
__date__ = "$Date: 2008-06-26 18:16:21 +0400 (Чтв, 26 Июн 2008) $"
 
from ks.interfaceswitcher.interfaces import IInterfaceSwitcherAble
from ng.content.article.interfaces import IDocFormatSwitcher

class IArticleDesignSwitcher(IInterfaceSwitcherAble):
    "Default Design"
    pass

    
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


class IDivisionDesignSwitcher(IInterfaceSwitcherAble):
    "Default Design"
    pass

class IDivisionDictionarySwitcher(IDivisionDesignSwitcher) :
    "Dictionary design "

class IDivisionItemSwitcher(IDivisionDesignSwitcher) :
    "Item design "
    
    
