### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 51517 2008-08-23 01:32:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51517 $"

from zope.viewlet import interfaces
from ng.skin.base.viewlet.viewletmain.interfaces import ICommonNewsListBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import INewsListBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import ICurrentBoxProvider
from ng.skin.greenpsy.viewletprofilemenu.interfaces import IProfileMenuBoxProvider
from ng.skin.greenpsy.viewletlogin.interfaces import ILoginBoxProvider
from ng.skin.greenpsy.viewletgoogleads.interfaces import IGoogleAdsBoxProvider

class IRightColumn(
    #IGoogleAdsBoxProvider,
    IProfileMenuBoxProvider, 
    ILoginBoxProvider,
    ICommonNewsListBoxProvider,
    INewsListBoxProvider, 
    interfaces.IViewletManager) :
    """ Right Column viewlet"""
                  
