### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: doctitle2titleadapter.py 49905 2008-01-08 16:20:57Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49905 $"

from zope.component import adapts
from ng.content.article.interfaces import IDocTitle
from ng.adapter.title.contained2titleadapter import Contained2TitleAdapter

class DocTitle2TitleAdapter(Contained2TitleAdapter) :

    adapts(IDocTitle)
    
    @property
    def title(self) :
        title = IDocTitle(self.context).title
        if not title :
            title = super(DocTitle2TitleAdapter,self).title        
        return title
