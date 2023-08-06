### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Search adapter for the Zope 3 neural content site

$Id: searchadapter.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"
__date__ = "$Date: 2008-06-26 18:16:21 +0400 (Чтв, 26 Июн 2008) $"
 
from zope.interface import Interface 

from interfaces import   ISearchClass, ISearchName, ISearchKeyword, ISearchBackName, ISearchBackKeyword
#from ng.app.remotefs.interfaces import IRemoteObject
from zope.cachedescriptors.property import Lazy
from os.path import normpath
from zope.security.proxy import removeSecurityProxy
from ng.adapter.mtime.interfaces import IMTime
from ng.adapter.path.interfaces import IPath
from pd.refchecker.refchecker import SearchReferenceAdapter
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation

def catch(f) :
    def c(self,*kv,**kw) :
        try :
            return f(self,*kv,**kw)
        except TypeError,msg :
            return u""
    return c            

class SearchAdapter(object) :
    """Interface for index objects"""

    @property
    @catch
    def klass(self) :
        return ISearchClass(self.ob).klass

    @property
    @catch
    def name(self) :
        return IPath(self.ob).tailpath

    @property
    @catch
    def names(self) :
        return self.searchname.names
    
    @Lazy
    def searchname(self) :
        return ISearchName(self.ob)

    @property
    @catch
    def keywords(self) :
        return "\n".join(self.keyword)
        
    @Lazy
    def keyword(self) :
        try :
            return [x.strip().lower() for x in IDictAnnotation(self.ob).keyword]
        except TypeError :
            return []            

    #@property
    #@catch
    #def path(self) :
    #    return normpath(self.remoteobject.path)

    #@property
    #@catch
    #def prefix(self) :
    #    return unicode(self.remoteobject.prefix)

    #@Lazy
    #def remoteobject(self) :
    #    return IRemoteObject(self.ob)

    @property
    @catch
    def backname(self) :
        return ISearchBackName(self).backname

    @property
    @catch
    def backkeyword(self) :
        return ISearchBackKeyword(self).backkeyword

    @property
    @catch
    def mtime(self) :
        return IMTime(self.ob).mtime
        
    @property
    @catch
    def urlpath(self) :
        return IPath(self.ob).path
        
    @property
    def reference(self) :
        return SearchReferenceAdapter(self).reference        
        
        
        
            
                