### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Class adapter for the Zope 3 based search package

$Id: searchnameadapter.py 49522 2007-12-18 07:39:29Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 49522 $"
__date__ = "$Date: 2007-12-18 10:39:29 +0300 (Втр, 18 Дек 2007) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field
import re

class SearchNameAdapter(object) :
    """Interface for index objects"""

    def __init__(self,ob) :
        self.name = [re.sub("\s+"," ",ob.__name__)]
        self.names = "\n".join(self.name)
        #]+ob.__name__.split(".")
