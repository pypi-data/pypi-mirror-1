### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of exceptiion

$Id: interfaces.py 53390 2009-07-08 11:01:43Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 53390 $"

from zope.interface import Interface
from zope.schema import Field

class IRenameException(Interface) :
    """ Basic Skin """

    ob = Field(title=u"New object")    