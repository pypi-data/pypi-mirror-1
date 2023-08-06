### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 52645 2009-02-16 23:33:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52645 $"

from zope.viewlet import interfaces
from ng.skin.base.viewlet.viewletmain.interfaces import INewsListBoxProvider
from ng.skin.base.viewlet.viewletsubscribe.interfaces import ISubscribeProvider
from ng.skin.base.viewlet.viewletmain.interfaces import ICurrentBoxProvider
from ng.skin.greenpsy.viewletmembers.interfaces import IMembersBoxProvider
from ng.skin.base.viewlet.viewlettopcommunities.interfaces import ITopCommunitiesBoxProvider
from ng.skin.greenpsy.viewletfastsearch.interfaces import IFastSearchBoxProvider
from ng.skin.base.viewlet.viewletrubriclist.interfaces import IRubricListProvider, IRubricCloudProvider, IRubricAllCloudProvider

class ILeftColumn(ISubscribeProvider,
                  ICurrentBoxProvider,
                  IMembersBoxProvider,
#                  ITopCommunitiesBoxProvider,
                  IFastSearchBoxProvider,
                  IRubricAllCloudProvider,
                  IRubricCloudProvider,
#                  IRubricListProvider,
                  interfaces.IViewletManager) :
    """ Left Column viewlet"""
