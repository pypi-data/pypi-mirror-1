### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 51850 2008-10-16 20:44:00Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51850 $"

from zope.viewlet import interfaces
from ng.skin.base.viewlet.viewletmain.interfaces import INewsListBoxProvider
from ng.skin.base.viewlet.viewletsubscribe.interfaces import ISubscribeProvider
from ng.skin.base.viewlet.viewletmain.interfaces import ICurrentBoxProvider
from ng.skin.greenpsy.viewletmembers.interfaces import IMembersBoxProvider
from ng.skin.greenpsy.viewlettopcommunities.interfaces import ITopCommunitiesBoxProvider
from ng.skin.greenpsy.viewletfastsearch.interfaces import IFastSearchBoxProvider
from ng.skin.greenpsy.viewletprofilemenu.interfaces import IProfileMenuBoxProvider
from ng.skin.greenpsy.viewletrubriclist.interfaces import IRubricListProvider

class ILeftColumn(ISubscribeProvider,
                  ICurrentBoxProvider,
                  IMembersBoxProvider,
#                  ITopCommunitiesBoxProvider,
                  IFastSearchBoxProvider,
                  IRubricListProvider,
                  interfaces.IViewletManager) :
    """ Left Column viewlet"""
