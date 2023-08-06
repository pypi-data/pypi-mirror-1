### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 52423 2009-01-31 16:34:40Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52423 $"

from zope.viewlet import interfaces
from ng.skin.base.viewlet.viewletmain.interfaces import ICommonNewsListBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import INewsListBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import ICurrentBoxProvider
from ng.skin.base.viewlet.viewlettoolbox.interfaces import IToolBoxProvider
from ng.skin.base.viewlet.viewletloginbox.interfaces import ILoginBoxProvider
from ng.skin.greenpsy.viewletgoogleads.interfaces import IGoogleAdsBoxProvider

class IRightColumn(
    #IGoogleAdsBoxProvider,
    IToolBoxProvider, 
    ILoginBoxProvider,
    ICommonNewsListBoxProvider,
    INewsListBoxProvider, 
    interfaces.IViewletManager) :
    """ Right Column viewlet"""
                  
