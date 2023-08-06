### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Class adapter for the Zope 3 based search package

$Id: searchclassadapter.py 1223 2007-03-03 01:37:10Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 1223 $"
__date__ = "$Date: 2007-03-03 04:37:10 +0300 (Сбт, 03 Мар 2007) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field

class SearchClassAdapter(object) :
    """Interface for index objects"""

    def __init__(self,ob) :
        self.klass = u"%s.%s" % ( ob.__class__.__module__,ob.__class__.__name__ )
