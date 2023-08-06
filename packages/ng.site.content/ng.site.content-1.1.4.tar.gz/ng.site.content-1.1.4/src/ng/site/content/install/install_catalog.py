### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InstallCatalog script for the Zope 3 based ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"

from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site

from zope.app.catalog.catalog import Catalog
from zope.app.catalog.interfaces import ICatalog

from zope.app.catalog.text import TextIndex
from zope.app.catalog.field import FieldIndex

from zc.catalog.catalogindex import SetIndex, ValueIndex 
from zc.catalog.interfaces import IIndexValues

from ng.site.content.search.interfaces import ISearch

def install_Catalog(context, **kw):
    """ Install Catalog """
    
    sm = context.getSiteManager()
    sm['Catalog'] = Catalog()
    sm.registerUtility(sm['Catalog'], provided=ICatalog)

    return "Success"

def install_Index(context, **kw) :
    """ Install all indexes """

    sm = context.getSiteManager()
    catalog = sm['Catalog'] 

    catalog['abstract'] = TextIndex(field_name=u'abstract',interface=ISearch, field_callable=False)
    catalog['backkeyword'] = SetIndex(field_name=u'backkeyword',interface=ISearch, field_callable=False)
    catalog['backname'] = SetIndex(field_name=u'backname',interface=ISearch, field_callable=False)
    catalog['body'] = TextIndex(field_name=u'body',interface=ISearch, field_callable=False)
    catalog['common'] = TextIndex(field_name=u'common',interface=ISearch, field_callable=False)
    catalog['keyword'] = SetIndex(field_name=u'keyword',interface=ISearch, field_callable=False)
    catalog['klass'] = FieldIndex(field_name=u'klass',interface=ISearch, field_callable=False)
    catalog['mtime'] = FieldIndex(field_name=u'mtime',interface=ISearch, field_callable=False)
    catalog['name'] = SetIndex(field_name=u'name',interface=ISearch, field_callable=False)
    catalog['reference'] = SetIndex(field_name=u'reference',interface=ISearch, field_callable=False)
    catalog['urlpath'] = FieldIndex(field_name=u'urlpath',interface=ISearch, field_callable=False)

    sm.registerUtility(catalog['backkeyword'],provided=IIndexValues,name='backkeyword')    
    sm.registerUtility(catalog['backname'],provided=IIndexValues,name='backname')    
    sm.registerUtility(catalog['keyword'],provided=IIndexValues,name='keyword')    

    return "Success"
