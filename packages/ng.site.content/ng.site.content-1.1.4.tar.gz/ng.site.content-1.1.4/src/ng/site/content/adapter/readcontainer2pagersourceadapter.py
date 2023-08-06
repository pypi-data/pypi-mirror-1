### -*- coding: utf-8 -*- #############################################
#######################################################################
""" OrderedContainer Adapter to IPagerSource Interface

$Id: readcontainer2pagersourceadapter.py 49905 2008-01-08 16:20:57Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49905 $"

from zope.interface import implements,Interface
from zope.component import adapts
from ng.adapter.pager.interfaces import IPagerSource
from zope.cachedescriptors.property import CachedProperty
from zope.app.container.interfaces import IReadContainer
from ng.content.article.adapter.containeradapter import ContentContainerAdapter

class ReadContainer2PagerSourceAdapter(ContentContainerAdapter):
    __doc__ = __doc__

    implements(IPagerSource)
    adapts(IReadContainer)

    def keys(self) :
        return list(super(ReadContainer2PagerSourceAdapter,self).keys())
        
