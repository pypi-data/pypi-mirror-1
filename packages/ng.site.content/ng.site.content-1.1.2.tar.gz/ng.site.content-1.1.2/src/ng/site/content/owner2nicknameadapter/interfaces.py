### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interface used to accept browser form of nickname from
author field.

$Id: interfaces.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"
 
from zope.interface import Interface

class IOwner2Nickname(Interface):

    def __call__(name):
        """Returns a nickname surround by link to profile for entered name"""

        