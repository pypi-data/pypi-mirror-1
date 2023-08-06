### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Class adapter for the Zope 3 based search package

$Id: searchbacknameadapter.py 51965 2008-10-23 21:55:22Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 51965 $"
__date__ = "$Date: 2008-10-24 01:55:22 +0400 (Птн, 24 Окт 2008) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field
import re


class SearchBackNameAdapter(object) :
    """Interface for index objects"""

    def __init__(self,ob) :
        self.backname = [re.sub("\s+"," ",x) for x in re.findall("\[name:(?P<name>[^:\]]+(?: :[^\]]+)?)",ob.common)]
