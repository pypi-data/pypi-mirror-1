### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installLogo script for the Zope 3 based ng.site.content.install package

$Id: install_logo.py 50586 2008-02-07 06:09:55Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50586 $"

from zope.app.file.interfaces import IImage
from zope.app.file.image import Image
from logo import logo

def installLogo(context, **kw):
    """ Создаёт в основной контейнере файл с логотипом сайта и именем logo
    """
    if kw[u'logo'].getSize() :
        context.logo = kw[u'logo']
    else :
        context.logo = Image(data=logo)
    return "Success"
