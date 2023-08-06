### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installObjectQueue script for the Zope 3 based
ng.site.content.install package

$Id: install_objectqueue.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"

from zope.app.file.interfaces import IImage
from zope.app.file.image import Image
from ng.app.objectqueue.interfaces import IObjectQueue
from ng.app.objectqueue.objectqueue import ObjectQueue

def installObjectQueue(context, **kw):
    """ Создаёт в сайт-менеджере ObjectQueue и регистрирует её под
        необходимым интерфейсом
    """
    sm = context.getSiteManager()
    
    oq = sm[u'objectqueue'] = ObjectQueue()
    
    sm.registerUtility(oq, provided=IObjectQueue)

    return "Success"
