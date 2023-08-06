### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Class adapter for the Zope 3 based search package

$Id: searchbacknameadapter.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"
__date__ = "$Date: 2008-10-21 23:07:20 +0400 (Втр, 21 Окт 2008) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field
import re


class SearchBackNameAdapter(object) :
    """Interface for index objects"""

    def __init__(self,ob) :
        self.backname = [re.sub("\s+"," ",x) for x in re.findall("\[name:(?P<name>[^:\]]+(?: :[^\]]+)?)",ob.common)]
