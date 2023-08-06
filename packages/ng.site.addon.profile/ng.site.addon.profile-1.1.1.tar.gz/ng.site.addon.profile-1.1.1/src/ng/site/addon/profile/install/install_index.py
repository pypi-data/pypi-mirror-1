### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InstallCatalog script for the Zope 3 based ng.site.content.install package

$Id: install_index.py 52177 2008-12-25 11:11:02Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52177 $"

from zope.app.catalog.text import TextIndex
from zope.app.catalog.field import FieldIndex
from zc.catalog.catalogindex import SetIndex

from ng.content.profile.profileannotation.interfaces import IProfileAnnotation

def install_Index(context, **kw):
    """ Install Indexes """
    
    sm = context.getSiteManager()
    catalog = sm['Catalog'] 

    catalog['email'] = TextIndex(field_name=u'email',interface=IProfileAnnotation, field_callable=False)
    catalog['nickname'] = TextIndex(field_name=u'nickname',interface=IProfileAnnotation, field_callable=False)
    catalog['profile'] = FieldIndex(field_name=u'userid',interface=IProfileAnnotation, field_callable=False)


    return "Success"
