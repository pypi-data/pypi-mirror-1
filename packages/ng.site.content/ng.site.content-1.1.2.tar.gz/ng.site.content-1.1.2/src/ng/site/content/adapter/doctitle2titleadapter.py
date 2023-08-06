### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: doctitle2titleadapter.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"

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
