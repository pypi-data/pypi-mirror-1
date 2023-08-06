### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RubricDescription class for the Zope 3 based ng.site.content.install package

$Id: rubricdescription.py 50586 2008-02-07 06:09:55Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50586 $"


from zope.interface import implements
from interfaces import IRubricDescription
from persistent import Persistent
from zope.schema import Field


class RubricDescription(object):
    """ RubricDescription
    """
    
    implements(IRubricDescription)
    
    name = u''
    
    title = u''
    
    abstract = u''
