### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installMain script for the Zope 3 based ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site
from zope.app.container.interfaces import IContainer


def installMain(context, **kw):
    """ Регистрирует context как папку Main, где впоследствии будет храниться
        содержимое сайта в виде экземпляров ng.content.article
    """
    context.title = kw['title']
    context.author = kw['author']
    
    sm = context.getSiteManager()
    sm.registerUtility(context, provided=IContainer, name=u'Main')

    return "Success"
