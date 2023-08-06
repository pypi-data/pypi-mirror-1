### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter article to rss-entry

$Id: article2rssentryadapter.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"

from zope.app.zapi import getUtility
from zope.component import ComponentLookupError
from zope.traversing.browser import absoluteURL
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.adapter.mtime.interfaces import IMTime
from persistent.interfaces import IPersistent
from zope.security.proxy import removeSecurityProxy
import uuid

class Article2RSSEntryAdapter(object) :
    """ Adapter article to rss-entry """
    def __init__(self,context,request) :
        ps = IPropertySheet(context)
        self.title = ps['title']
        self.updated = IMTime(context).strftime("%Y-%m-%dT%H-%M-%SZ")
        self.summary = ps['summary'] or ps['autosummary']
        self.id = uuid.uuid3(uuid.NAMESPACE_OID,IPersistent(removeSecurityProxy(context))._p_oid).urn
        self.link = absoluteURL(context,request)


    title = ""
    updated = ""
    summary = ""
    id = ""
    link = ""
    
