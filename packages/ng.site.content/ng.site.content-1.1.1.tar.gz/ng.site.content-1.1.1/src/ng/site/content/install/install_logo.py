### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installLogo script for the Zope 3 based ng.site.content.install package

$Id: install_logo.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"

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
