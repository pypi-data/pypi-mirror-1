### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Search adapter for the Zope 3 neural content site

$Id: photosearchadapter.py 52128 2008-12-23 08:42:10Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51189 $"
__date__ = "$Date: 2008-06-26 15:21:11 +0400 (Чтв, 26 Июн 2008) $"
 
from zope.interface import Interface 
from zope.cachedescriptors.property import Lazy
from ng.content.article.interfaces import IDocShort
from ng.site.content.search.searchadapter import SearchAdapter

class PhotoSearchAdapter(SearchAdapter) :
    """Interface for index objects"""

    @Lazy
    def iface(self) :
        return IDocShort(self.ob)

    @property
    def title(self) :
        return self.iface.title

    @property
    def abstract(self) :
        return self.iface.abstract

    
                    
        
            
                