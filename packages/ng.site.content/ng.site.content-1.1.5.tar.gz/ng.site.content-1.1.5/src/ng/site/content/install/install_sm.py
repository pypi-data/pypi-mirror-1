### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installSiteManager script for the Zope 3 based ng.site.content.install
package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site


def installSiteManager(context, **kw):
    """ Преобразует папку контекста в сайт
    """
    # Создаём локальный менеджер сайта
    sm = site.LocalSiteManager(context)
    # Устанавливаем созданный менеджер сайта в контекст
    context.setSiteManager(sm)
    # Делаем контекст сайтом
    setSite(context)
    # Выполнено успешно
    return "Success"
