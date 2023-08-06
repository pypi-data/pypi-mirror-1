### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ErrorView - is base class for zope3 errors

$Id: renameview.py 53390 2009-07-08 11:01:43Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53390 $"

from zope.publisher.browser import BrowserView
from zope.app.exception.systemerror import SystemErrorView
from zope.traversing.browser.absoluteurl import absoluteURL

class RenameView(BrowserView,SystemErrorView) :
    """Class for redirect view """
    def __init__(self,context,request) :
        super(RenameView,self).__init__(context,request)
        request.response.redirect(absoluteURL(context.ob,request) "/@@commonedit.html")

    def __call__(self,*kv) :
      return "Please, wait"
      