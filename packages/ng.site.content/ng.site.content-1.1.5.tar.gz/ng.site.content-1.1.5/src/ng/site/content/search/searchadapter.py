### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Search adapter for the Zope 3 neural content site

$Id: searchadapter.py 53379 2009-07-05 20:49:33Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 53379 $"
__date__ = "$Date: 2009-07-06 00:49:33 +0400 (Пнд, 06 Июл 2009) $"
 
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
from ng.content.article.interfaces import IDocShort

import re
rspace = re.compile("\s+",re.U)

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
        try :
            title = (IDocShort(self.ob).title.lower(),)
        except TypeError,msg :
            print msg
            title = ()            
        return [ re.sub(rspace," ",x).strip() for x in  IPath(self.ob).tailpath + title ]
        
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
            return [re.sub(rspace," ",x.strip()).lower() for x in IDictAnnotation(self.ob).keyword]
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
        
        
        
            
                