### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installRegistry script for the Zope 3 based ng.site.content.install package

$Id: install_registry.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"


from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from ng.app.registry.registry import Registry
from ng.app.registry.registryint import RegistryInt
from ng.app.registry.registrytextline import RegistryTextLine
from ng.app.registry.interfaces import IRegistry


def installRegistry(context, **kw):
    """ Устанавливает в сайт-менеджере продукт ng.app.registry, регистрируем
        его и наполняем необходимым содержимым
    """
    sm = context.getSiteManager()
    sm[u'registry'] = Registry()
    sm.registerUtility(sm[u'registry'], provided=IRegistry)
    
    sm[u'registry'][u'pager_orphan'] = RegistryInt()
    sm[u'registry'][u'pager_orphan'].data = 3
    
    sm[u'registry'][u'pager_size'] = RegistryInt()
    sm[u'registry'][u'pager_size'].data = 10
    ## sm[u'registry'][u'pager_revert'] = RegistryBool()

    sm[u'registry'][u'pager_rss'] = RegistryTextLine()
    sm[u'registry'][u'pager_size'].data = '@@rssview.html'

    sm[u'registry'][u'datetimeformat'] = RegistryTextLine()
    sm[u'registry'][u'datetimeformat'].data = '%Y-%m-%d %H:%M'
    
    return "Success"
