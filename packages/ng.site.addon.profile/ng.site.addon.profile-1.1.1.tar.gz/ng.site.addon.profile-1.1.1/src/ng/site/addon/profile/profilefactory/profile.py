### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Factory used to create Profile 

$Id: profile.py 52429 2009-01-31 16:38:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50550 $"
 
from zope.interface import implements, implementedBy
from zope.interface import alsoProvides
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager

from zope.app.zapi import getUtility
from zope.app.container.interfaces import IContainer 

from ng.content.article.interfaces import IDocShortLogo
from ng.content.article.division.division import Division
from ng.content.profile.profileannotation.interfaces import IProfileAnnotationAble, IProfileAnnotation
from zope.security.proxy import removeSecurityProxy
from ng.app.objectqueue.interfaces import  IObjectQueueAnnotation
from zope.component.factory import Factory

def ProfileCreate(principal) :
    division = Division()
    alsoProvides(division, IProfileAnnotationAble)
    alsoProvides(division, IDocShortLogo)
    IProfileAnnotation(division).userid=principal
    return division


def Profile(context) :
    return ProfileCreate(removeSecurityProxy(context).request.form['field.userid'])

profilefactory = Factory(
    Profile,
    title=u"User Profile",
    description=u"Factory used to create Division-based User Profile",
    interfaces=implementedBy(Division))


def create_profile_handle(ob,event) :
    oqa = IObjectQueueAnnotation(ob)
    oqa.order = u'straight'
    oqa.maxlen = 40

    principal = IProfileAnnotation(ob).userid
    principal_perms = IPrincipalPermissionManager(ob)
    principal_perms.grantPermissionToPrincipal('zope.ManageContent', principal)
    principal_perms.grantPermissionToPrincipal('smartimage.Edit', principal)

    root_perms = IPrincipalPermissionManager(getUtility(IContainer,name='Main'))
    
    root_perms.grantPermissionToPrincipal("dreambot.ProfileServices",principal)
    root_perms.grantPermissionToPrincipal("dreambot.ObjectQueueHandle",principal)


