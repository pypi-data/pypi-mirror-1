### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interface used to accept browser form of nickname from
author field.

$Id: interfaces.py 51718 2008-09-15 23:35:15Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51718 $"
 
from zope.interface import Interface

class IProfile(Interface):

    def __call__(name):
        """Returns a nickname surround by link to profile for entered name"""

        