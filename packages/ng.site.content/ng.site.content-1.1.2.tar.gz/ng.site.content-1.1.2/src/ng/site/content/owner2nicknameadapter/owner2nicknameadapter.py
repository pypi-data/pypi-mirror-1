### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter owner to nickname in browse represetative

$Id: owner2nicknameadapter.py 51921 2008-10-21 19:07:20Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51921 $"

from ng.skin.base.page.contentlet.viewletbase import ViewletBase
from ng.content.comment.interfaces import ICommentAnnotation
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from ng.content.annotation.profileannotation.interfaces import IProfileAnnotation

class Owner2NicknameAdapter(object) :
    """ Owner 2 nickname adapter """

    def __init__(self,context,request) :
        self.context = context
        self.request = request
        
    def __getitem__(self,author) :
      print 'qq', author
      for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( unicode(author), unicode(author) )
                          ) :
          print "Profile", profile, author, type(author), self.context
          return """<a class="nickname" href="%(href)s"> %(author)s</a>""" % {
                    "author" : IProfileAnnotation(profile).nickname,
                    "href" : adaptiveURL(profile,self.request)
                  }
      else :
          return """%(author)s""" % { 'author' : author }

