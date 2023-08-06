### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Class adapter for the Zope 3 based search package

$Id: searchclassadapter.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"
__date__ = "$Date: 2008-06-26 18:16:21 +0400 (Чтв, 26 Июн 2008) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field

class SearchClassAdapter(object) :
    """Interface for index objects"""

    def __init__(self,ob) :
        self.klass = u"%s.%s" % ( ob.__class__.__module__,ob.__class__.__name__ )
