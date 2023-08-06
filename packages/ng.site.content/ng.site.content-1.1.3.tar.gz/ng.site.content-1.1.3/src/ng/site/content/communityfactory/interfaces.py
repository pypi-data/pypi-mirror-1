### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.site package,
community factory.

$Id: interfaces.py 51965 2008-10-23 21:55:22Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51965 $"
 

from zope.schema import Field
from zope.interface import Interface
from ng.site.greenpsy.wave.interfaces import ITagRubricAnnotationAblePropagate

class ICommunityAnnotable(Interface) :
    """ """    

def forbidden(container) :
    print "ICA",container
    if ICommunityAnnotable.providedBy(container) :
        print False
        return False
    #elif ITagRubricAnnotationAblePropagate.providedBy(container) :
    #    return False
    return True

class ICommunityAnnotableForbidden(Interface) :
    __parent__ = Field(constraint = forbidden)

    