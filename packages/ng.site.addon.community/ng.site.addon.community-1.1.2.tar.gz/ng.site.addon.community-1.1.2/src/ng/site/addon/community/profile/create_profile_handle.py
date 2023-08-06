### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Creation handle used to treat profile for use with comunity

$Id: create_profile_handle.py 52428 2009-01-31 16:37:49Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52428 $"
 
from zope.interface import implements
from zope.interface import alsoProvides
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager

from zope.app.zapi import getUtility
from zope.app.container.interfaces import IContainer 

from ng.content.profile.friendshipannotation.interfaces import IFriendshipAnnotationAble, IFriendshipAnnotation
from ng.content.profile.friendobjectqueueannotation.interfaces import IFriendObjectQueueAnnotationAble, IFriendObjectQueueAnnotation
from ng.content.profile.exchangeannotation.interfaces import IExchangeAnnotationAble


def create_profile_handle(ob,event) :
    alsoProvides(ob, IFriendObjectQueueAnnotationAble)
    alsoProvides(ob, IFriendshipAnnotationAble)
    alsoProvides(ob, IExchangeAnnotationAble)

    oqa = IFriendObjectQueueAnnotation(ob) 
    oqa.order = u'straight'
    oqa.maxlen = 40
    
