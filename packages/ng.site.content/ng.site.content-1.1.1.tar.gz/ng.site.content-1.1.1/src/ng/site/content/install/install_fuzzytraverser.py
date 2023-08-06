### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installFuzzyTraverser script for the Zope 3 based
ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from ng.fuzzytraverser.fuzzytraverserproperties.fuzzytraverserproperties import FuzzyTraverserProperties
from ng.fuzzytraverser.fuzzytraverserproperties.interfaces import IFuzzyTraverserProperties


def installFuzzyTraverser(context, **kw):
    """ Install FuzzyTraverserProperty into site manager """

    sm = context.getSiteManager()
    sm[u'FuzzyTraverserProperties'] = FuzzyTraverserProperties()
    sm[u'FuzzyTraverserProperties'].on  = True
    sm[u'FuzzyTraverserProperties'].use = True
    
    sm.registerUtility(sm[u'FuzzyTraverserProperties'], provided=IFuzzyTraverserProperties)

    return "Success"
