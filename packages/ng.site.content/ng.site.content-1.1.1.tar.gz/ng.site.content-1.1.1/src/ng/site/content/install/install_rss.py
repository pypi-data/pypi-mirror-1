### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installRSS script for the Zope 3 based ng.site.content.install package

$Id: install_rss.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"

from zope.app.file.interfaces import IImage
from zope.app.file.image import Image
from ng.app.rss.interfaces import IRSS
from ng.app.rss.rss import RSS

def installRSS(context, **kw):
    """ Создаёт в сайт-менеждере RSS и регистрирует его
    """
    sm = context.getSiteManager()
    
    rss = sm[u'RSS'] = RSS()
    
    sm.registerUtility(sm[u'RSS'], provided=IRSS)
    
    return "Success"
