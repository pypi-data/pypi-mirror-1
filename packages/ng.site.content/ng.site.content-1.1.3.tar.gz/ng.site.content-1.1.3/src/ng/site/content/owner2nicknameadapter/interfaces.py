### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interface used to accept browser form of nickname from
author field.

$Id: interfaces.py 51965 2008-10-23 21:55:22Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51965 $"
 
from zope.interface import Interface

class IOwner2Nickname(Interface):

    def __call__(name):
        """Returns a nickname surround by link to profile for entered name"""

        