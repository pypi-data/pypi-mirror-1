### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installAbout, installArticles, installMirrors, installNews, installRubric
and installRubrics scripts for the Zope 3 based ng.site.content.install package

$Id: install_auth.py 52177 2008-12-25 11:11:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52177 $"

from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site
from zope.app.authentication.authentication import PluggableAuthentication
from ng.app.openid.openidauthenticator import OpenIDAuthenticatorPlugin
from ng.app.openid.openidcredentials import OpenIDCredentialsPlugin
from ng.app.openid.logincredentials import LoginCredentialsPlugin
from ng.app.openid.cookiecredentials import CookieCredentialsPlugin
from ng.app.openid.interfaces import ICookieCredentialsPlugin
from zope.app.security.interfaces import IAuthentication 
def install_PAM(context, **kw):
    """ Создаёт раздел Profiles
    """
    sm = context.getSiteManager()
    ob = sm['openid'] = PluggableAuthentication(prefix=kw["pam_prefix"])
    sm.registerUtility(ob, provided=IAuthentication)

    return "Success"

def install_OpenIdAuthenticator(context, **kw):
    """ Create openid authenticator plugin """
    openid = context.getSiteManager()['openid']
    ob = openid['OpenIDAuthenticatorPlugin'] = OpenIDAuthenticatorPlugin()
    ob.prefix = kw["pam_prefix"]
    ob.profile = kw["pam_redirect"]
    openid.authenticatorPlugins = ('OpenIDAuthenticatorPlugin',)

    return "Success"
    
def install_OpenIdCredentials(context, **kw):
    """ Create openid session plugin """
    openid = context.getSiteManager()['openid']
    ob = openid['OpenIDCredentialsPlugin'] = OpenIDCredentialsPlugin()
    ob.vh_path = kw['vh_path'] 
    ob.vh_site = kw['vh_site'] 
    openid.credentialsPlugins += ('OpenIDCredentialsPlugin',)

    return "Success"

def install_LoginCredentials(context, **kw):
    """ Create login session plugin """
    openid = context.getSiteManager()['openid']
    ob = openid['LoginCredentialsPlugin'] = LoginCredentialsPlugin()
    ob.vh_path = kw['vh_path'] 
    ob.vh_site = kw['vh_site'] 
    ob.prefix = kw["pam_prefix"]
    openid.credentialsPlugins += ('LoginCredentialsPlugin',)

    return "Success"

def install_CookieCredentials(context, **kw):
    """ Create openid session plugin """
    sm = context.getSiteManager()
    openid = sm['openid']
    ob = openid['CookieCredentialsPlugin'] = CookieCredentialsPlugin()
    ob.vh_path = kw['vh_path'] 
    ob.vh_site = kw['vh_site'] 
    openid.credentialsPlugins += ('CookieCredentialsPlugin',)
    sm.registerUtility(ob, provided=ICookieCredentialsPlugin)

    return "Success"
                