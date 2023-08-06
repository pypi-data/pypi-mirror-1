### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installIntIds script for the Zope 3 based ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds


def installIntIds(context, **kw):
    """ Устанавливает в сайт-менеджере контекста генератор уникальных
        идентификаторов (IntIds) и регистрирует его
    """
    # Получаем сайт-менеджер
    sm = context.getSiteManager()
    # Добавляем в сайт-менеджер утилиту IntIds (генератор уникальных
    # идентификаторов)
    sm[u'IntIds'] = IntIds()
    # Регистрируем добавленную утилиту без имени с интерфейсом IIntIds
    sm.registerUtility(sm[u'IntIds'], provided=IIntIds)
    # Регистрируем добавленную утилиту с интерфейсом IIntIds и именем intid
    sm.registerUtility(sm[u'IntIds'], provided=IIntIds, name=u'intid')
    sm[u'IntIds'].register(context)

    return "Success"
