### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Factories for division class used as community

$Id: community.py 52428 2009-01-31 16:37:49Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52428 $"
 
from zope.interface import implements
from ng.content.article.division.division import Division
from ng.content.profile.friendshipannotation.interfaces import IFriendshipAnnotationAble, IFriendshipAnnotation
from ng.content.article.interfaces import IDocShortLogo
from zope.security.proxy import removeSecurityProxy
from zope.interface import alsoProvides
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from ng.app.objectqueue.interfaces import  IObjectQueueAnnotation
from ng.content.profile.communityobjectqueueannotation.interfaces import ICommunityObjectQueueAnnotationAble, ICommunityObjectQueueAnnotation
from ng.content.comment.interfaces import ICommentAnnotationAble
from interfaces import ICommunityAnnotable


from zope.app.zapi import getUtility
from zope.app.container.interfaces import IContainer 

def CommunityCreate(principal) :
    division = Division()
    alsoProvides(division, IFriendshipAnnotationAble)
    alsoProvides(division, IDocShortLogo)
    alsoProvides(division, ICommunityObjectQueueAnnotationAble)
    alsoProvides(division, ICommunityAnnotable)
    alsoProvides(division, ICommentAnnotationAble)

    for oqa in IObjectQueueAnnotation(division), ICommunityObjectQueueAnnotation(division) :
        oqa.order = u'straight'
        oqa.maxlen = 40

    IObjectQueueAnnotation(division).use = False
    
    principal_perms = IPrincipalPermissionManager(division)
    principal_perms.grantPermissionToPrincipal('zope.ManageContent', principal)
    principal_perms.grantPermissionToPrincipal('smartimage.Edit', principal)

    root_perms = IPrincipalPermissionManager(getUtility(IContainer,name='Main'))
    
    root_perms.grantPermissionToPrincipal("dreambot.ProfileServices",principal)
    root_perms.grantPermissionToPrincipal("dreambot.AddComment",principal)
    root_perms.grantPermissionToPrincipal("dreambot.ObjectQueueHandle",principal)

    return division


def Community(context) :
    return CommunityCreate(context.request.principal.id)
    