### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installObjectQueue script for the Zope 3 based
ng.site.content.install package

$Id: install_quota.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"

from zope.app.file.interfaces import IImage
from zope.app.file.image import Image
from ng.app.quota.interfaces import IQuota
from ng.app.quota.quota import Quota

def installQuota(context, **kw):
    """ Создаёт в сайт-менеджере Quota и регистрирует её под
        необходимым интерфейсом
    """
    sm = context.getSiteManager()
    
    quota = sm[u'quota'] = Quota()
    
    sm.registerUtility(quota, provided=IQuota)

    return "Success"
