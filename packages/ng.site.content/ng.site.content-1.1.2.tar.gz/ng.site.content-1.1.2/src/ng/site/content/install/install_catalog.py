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

def installCatalog(context, **kw):
    """ Install Catalog and all indexes that them need """
    
    sm = context.getSiteManager()
    sm['Catalog'] = Catalog()
    sm.registerUtility(sm['Catalog'], provided=ICatalog, name='catalog')

    sm['Catalog']['abstract'] = TextIndex(field_name=u'abstract', interface=ISearch, field_callable=False)
    sm['Catalog']['backkeyword'] = SetIndex(field_name=u'backkeyword',interface=ISearch, field_callable=False)
    sm['Catalog']['backname'] = SetIndex(field_name=u'backname',interface=ISearch, field_callable=False)
    sm['Catalog']['body'] = TextIndex(field_name=u'body', interface=ISearch, field_callable=False)
    sm['Catalog']['common'] = TextIndex(field_name=u'common', interface=ISearch, field_callable=False)
    sm['Catalog']['keyword'] = SetIndex(field_name=u'keyword',interface=ISearch, field_callable=False)
    sm['Catalog']['klass'] = FieldIndex(field_name=u'klass', interface=ISearch, field_callable=False)
    sm['Catalog']['mtime'] = FieldIndex(field_name=u'mtime', interface=ISearch, field_callable=False)
    sm['Catalog']['name'] = SetIndex(field_name=u'name', interface=ISearch, field_callable=False)
    sm['Catalog']['reference'] = SetIndex(field_name=u'reference',interface=ISearch, field_callable=False)
    sm['Catalog']['urlpath'] = FieldIndex(field_name=u'urlpath',interface=ISearch, field_callable=False)

    sm.registerUtility(sm['Catalog']['backkeyword'],provided=IIndexValues,name='backkeyword')    
    sm.registerUtility(sm['Catalog']['backname'],provided=IIndexValues,name='backname')    
    sm.registerUtility(sm['Catalog']['keyword'],provided=IIndexValues,name='keyword')    

    return "Success"
