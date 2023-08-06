### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter article to rss-entry

$Id: article2rssentryadapter.py 52181 2008-12-25 11:15:40Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52181 $"

from zope.app.zapi import getUtility
from zope.component import ComponentLookupError
from zope.traversing.browser import absoluteURL
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.adapter.mtime.interfaces import IMTime
from persistent.interfaces import IPersistent
from zope.security.proxy import removeSecurityProxy
import uuid
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from ng.content.profile.profileannotation.interfaces import IProfileAnnotation

class Article2RSSEntryAdapter(object) :
    """ Adapter article to rss-entry """
    def __init__(self,context,request) :
        ps = IPropertySheet(context)
        self.title = ps['title']
        self.updated = IMTime(context).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.summary = ps['summary'] or ps['autosummary']
        self.id = uuid.uuid3(uuid.NAMESPACE_OID,IPersistent(removeSecurityProxy(context))._p_oid).urn
        self.link = absoluteURL(context,request)
        for profile in getUtility(ICatalog,context=context) \
                            .searchResults(
                                profile=( unicode(context.author), unicode(context.author) )
                            ) :
            self.author = IProfileAnnotation(profile).nickname
        else :
            self.author = context.author or ""

    title = ""
    updated = ""
    summary = ""
    id = ""
    link = ""
    author = ""    
