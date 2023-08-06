### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InstallBanner script for the Zope 3 based ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"

from zope.app.component.hooks import setSite
from zope.app.component import site
from ng.app.smartbanner.smartbannercontainer.smartbannercontainer import SmartBannerContainer
from ng.app.smartbanner.smartbanner.smartbanner import SmartBanner
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer
from logo import banners

def installBanner(context, **kw):
    """ Добавляет в сайт-менеджер папку banner и помещает в неё все
        необходимые баннеры
    """
    sm = context.getSiteManager()
    bc = sm[u'banner'] = SmartBannerContainer()
    for name,data,url,alt in banners :
        banner = bc[name] = SmartBanner(data=data)
        banner.alt = alt
        banner.url = url   

    sm.registerUtility(sm[u'banner'], provided=ISmartBannerContainer)

    return "Success"
