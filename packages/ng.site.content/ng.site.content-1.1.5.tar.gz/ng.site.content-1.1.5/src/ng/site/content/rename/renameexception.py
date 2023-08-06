### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ErrorView - is base class for zope3 errors

$Id: renameexception.py 53390 2009-07-08 11:01:43Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53390 $"


from zope.interface import implements
from interfaces import IRenameException

class RenameException(Exception) :
    implements(IRenameException)
    
    def __init__(self,ob) :
        self.ob = ob
        self.args = [ob]        