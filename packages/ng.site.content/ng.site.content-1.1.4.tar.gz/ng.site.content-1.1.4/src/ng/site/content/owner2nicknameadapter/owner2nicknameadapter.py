### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter owner to nickname in browse represetative

$Id: owner2nicknameadapter.py 52560 2009-02-11 20:08:02Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52560 $"

from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from ng.content.profile.profileannotation.interfaces import IProfileAnnotation

class Owner2NicknameAdapter(object) :
    """ Owner 2 nickname adapter """

    def __init__(self,context,request) :
        self.context = context
        self.request = request
        
    def __getitem__(self,author) :
      if author is None :
         return u""
         
      for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( unicode(author), unicode(author) )
                          ) :
          return """<a class="nickname" href="%(href)s"> %(author)s</a>""" % {
                    "author" : IProfileAnnotation(profile).nickname,
                    "href" : adaptiveURL(profile,self.request)
                  }
      else :
          return """%(author)s""" % { 'author' : author }

