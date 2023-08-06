### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Statistic class for the Zope 3 based ng.skin.greenpsy package

$Id: profileadapter.py 51965 2008-10-23 21:55:22Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51965 $"

from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog

def profileadapter(context,request) :
    return profilesearch(context,request.principal.id)


def profilesearch(context,principalid) :
    return iter(getUtility(ICatalog,context=context) \
                          .searchResults(
                               profile=( principalid, principalid )
                          )).next()

from zope.security.management import queryInteraction                          

def profileadaptersimple(context) :
    interaction = queryInteraction()
    if interaction is not None :
        for participation in interaction.participations :
            principalid = participation.principal.id
            try :
              print "SIMPLE",principalid
              return profilesearch(context,principalid) 
            except StopIteration :
              pass
              
                              