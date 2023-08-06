### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Class adapter for the Zope 3 based search package

$Id: searchbacknameadapter.py 53379 2009-07-05 20:49:33Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 53379 $"
__date__ = "$Date: 2009-07-06 00:49:33 +0400 (Пнд, 06 Июл 2009) $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Tuple, Set, Field
import re


class SearchBackNameAdapter(object) :
    """Interface for index objects"""

    def __init__(self,ob) :
        backname = [re.sub("\s+"," ",x).strip() for x in re.findall("\[name:(?P<name>[^:\]]+(?: :[^\]]+)?)",ob.common)]
        self.backname = backname + [ x.lower() for x in backname ]
