### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for main page with news.

$Id: main.py 52287 2009-01-11 15:55:05Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52287 $"

from zope.app import zapi
from zope.app.container.interfaces import IContainer

class Blog(object) :

    @property
    def news(self) :
        try :
            return zapi.getUtility(IContainer,name='profile',context=self.context)
        except LookupError :
            return self.context
                                       
        
