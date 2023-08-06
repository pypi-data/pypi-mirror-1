### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 52446 2009-02-02 13:41:19Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52446 $"

from zope.viewlet import interfaces
from ng.skin.base.viewlet.viewlettoolbox.interfaces import IToolBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import INewsListBoxProvider
from ng.skin.base.viewlet.viewletloginbox.interfaces import ILoginBoxProvider
from ng.skin.base.viewlet.viewletrubriclist.interfaces import IRubricAllCloudProvider

class IColumn( 
    INewsListBoxProvider, 
    ILoginBoxProvider, 
    IRubricAllCloudProvider,
    interfaces.IViewletManager) :
    """ Column viewlet provider """



    