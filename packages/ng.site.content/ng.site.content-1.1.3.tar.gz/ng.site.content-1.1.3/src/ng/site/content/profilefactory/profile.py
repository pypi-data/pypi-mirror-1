### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Factories for article class used in wiki

$Id: profile.py 51965 2008-10-23 21:55:22Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50550 $"
 
from zope.interface import implements
from ng.content.article.division.division import Division
from ng.content.annotation.profileannotation.interfaces import IProfileAnnotationAble, IProfileAnnotation
from ng.content.annotation.friendshipannotation.interfaces import IFriendshipAnnotationAble, IFriendshipAnnotation
from ng.content.article.interfaces import IDocShortLogo
from zope.security.proxy import removeSecurityProxy
from zope.interface import alsoProvides
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from ng.app.objectqueue.interfaces import  IObjectQueueAnnotation
from ng.content.annotation.friendobjectqueueannotation.interfaces import IFriendObjectQueueAnnotationAble, IFriendObjectQueueAnnotation
from ng.content.profile.exchangeannotation.interfaces import IExchangeAnnotationAble

from zope.app.zapi import getUtility
from zope.app.container.interfaces import IContainer 


def ProfileCreate(principal) :
    division = Division()
    alsoProvides(division, IProfileAnnotationAble)
    alsoProvides(division, IFriendshipAnnotationAble)
    alsoProvides(division, IDocShortLogo)
    alsoProvides(division, IFriendObjectQueueAnnotationAble)
    alsoProvides(division, IExchangeAnnotationAble)

    for oqa in IObjectQueueAnnotation(division), IFriendObjectQueueAnnotation(division) :
        oqa.order = u'straight'
        oqa.maxlen = 40
    
    IProfileAnnotation(division).userid=principal
    principal_perms = IPrincipalPermissionManager(division)
    principal_perms.grantPermissionToPrincipal('zope.ManageContent', principal)
    principal_perms.grantPermissionToPrincipal('smartimage.Edit', principal)

    root_perms = IPrincipalPermissionManager(getUtility(IContainer,name='Main'))
    
    root_perms.grantPermissionToPrincipal("dreambot.ProfileServices",principal)
    root_perms.grantPermissionToPrincipal("dreambot.AddComment",principal)
    root_perms.grantPermissionToPrincipal("dreambot.ObjectQueueHandle",principal)

    return division


def Profile(context) :
    print "Profile", context
    return ProfileCreate(context.request.form['field.userid'])
    