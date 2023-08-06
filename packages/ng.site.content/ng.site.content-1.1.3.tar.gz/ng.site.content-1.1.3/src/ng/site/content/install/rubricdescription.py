### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RubricDescription class for the Zope 3 based ng.site.content.install package

$Id: rubricdescription.py 51965 2008-10-23 21:55:22Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51965 $"


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
