### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installAbout, installArticles, installMirrors, installNews, installRubric
and installRubrics scripts for the Zope 3 based ng.site.content.install package

$Id: install_content.py 52152 2008-12-23 19:45:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52152 $"

from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site

from ng.content.article.division.division import Division
from ng.content.article.article.article import Article
from ng.app.objectqueue.interfaces import IObjectQueueAnnotation
from zope.app.container.interfaces import IContainer

def install_Profile(context, **kw):
    """ Create division named Profile """
    
    profile = context[u'profile'] = Division()

    profile.title = kw['profile']
    profile.abstract = u''
    profile.author = kw['author']

    sm = context.getSiteManager()
    sm.registerUtility(context[u'profile'], provided=IContainer, name=u'profile')
    IObjectQueueAnnotation(profile).use = True
    IObjectQueueAnnotation(profile).islast = False

    return "Success"
