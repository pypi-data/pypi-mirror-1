### -*- coding: utf-8 -*- #############################################
######################################################################

# Make it a Python package

import os.path
all = ['logo', 'banners' ]
logo = open(os.path.join(__path__[0],'nuclearpig_logo_demo.gif')).read()

def bannertuple(name,url,alt) :
    return (unicode(name),open(os.path.join(__path__[0],name)).read(),url,unicode(alt))

banner_zope =  bannertuple('banner_zope.gif','http://www.zope.org','Zope')
banner_thedream_whiteblue = bannertuple('banner_thedream_whiteblue.png','http://deambot.org','The Dream Bot Info Site')
banners = [ banner_zope, banner_thedream_whiteblue]