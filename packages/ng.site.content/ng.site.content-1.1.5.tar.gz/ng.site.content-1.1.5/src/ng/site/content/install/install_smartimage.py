### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installSmartImage script for the Zope 3 based ng.site.content.install
package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site

from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from ks.smartimage.smartimagecache.smartimagecache import SmartImageCache
from ks.smartimage.smartimagecache.scale import Scale


def installSmartImage(context, **kw):
    """ Устанавливает и настраивает продукт SmartImage
    """
    sm = context.getSiteManager()
    
    sm[u'SmartImageCache'] = SmartImageCache()
    
    sic = sm[u'SmartImageCache']

    sic.scales = (Scale(u'small', 40, 50), Scale(u'big', 400, 500),)

    sic.format = u'GIF'
    sic.scale = u'big'
    sic.basepath = u'/' + context.__name__

    sm.registerUtility(sm[u'SmartImageCache'], provided=ISmartImageProp)

    return "Success"
