### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Interfaces for the Zope 3 based search package

$Id: interfaces.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"
__date__ = "$Date: 2008-10-21 23:07:20 +0400 (Втр, 21 Окт 2008) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field

class ISearchable(Interface) :
    """ Interface for searchable objects """

class ISearchClass(Interface) :
    """Interface for index objects"""

    klass = Text()

class ISearchName(Interface) :
    """Interface for index objects"""

    name = Text()

class ISearchBackName(Interface) :
    """Interface for index objects"""

    backname = Text()

class ISearchBackKeyword(Interface) :
    """Interface for index objects"""

    backkeyword = Text()

class ISearchKeyword(Interface) :
    """Interface for index objects"""

    keyword = Text()
                
class ISearch(Interface) :
    """ Interface for common object search """

    title = Text()
    
    abstract = Text()
    
    body = Text()
    
    common = Text()

    keywords = Text()

    klass = Text()

    name = Text()

    prefix = Text()
    
    path = Text()

    backname = Text()            

    mtime = Datetime()

    urlpath = Text()

    reference = Tuple()        
    