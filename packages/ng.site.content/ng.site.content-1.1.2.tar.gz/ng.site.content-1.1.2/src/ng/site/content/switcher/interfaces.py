### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Dwitchable markers

$Id: interfaces.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"
__date__ = "$Date: 2008-10-21 23:07:20 +0400 (Втр, 21 Окт 2008) $"
 
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
    
    
