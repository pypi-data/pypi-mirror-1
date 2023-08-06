### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FriendList class for the Zope 3 based ng.skin.greenpsy package

$Id: friendlist.py 52235 2008-12-27 22:59:22Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52235 $"

from ng.content.profile.friendshipannotation.browser.friendlist import FriendList
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from ng.site.addon.community.communityfactory.interfaces import ICommunityAnnotable

class FriendList(FriendList) :

    page = ViewPageTemplateFile("friendlist.pt")
    pageedit = ViewPageTemplateFile("friendlistedit.pt")
    
    def empty(self,*kv,**kw) :
        return self.pageedit(self,error=u'You must select one item to edit', *kv, **kw)

    def multiaccepted(self, ids=[], *kv, **kw) :
        if not ids :
            return self.empty(*kv,**kw)

        for i in ids:
            self.agree(i)
        return self.pageedit(self,message=u'Friendship suggestion accepted', *kv, **kw)
        
    def multirejected(self, ids=[], *kv, **kw) :
        if not ids :
            return self.empty(*kv,**kw)

        for i in ids:
            self.reject(i)
        return self.pageedit(self,message=u'Friendship suggestion rejected', *kv, **kw)

    def multiremove(self, ids=[], *kv, **kw) :
        if not ids :
            return self.empty(*kv,**kw)

        for i in ids:
            self.remove(i)
        return self.pageedit(self,message=u'Friendship denied', *kv, **kw)

    def iscommunity(self,profile) :
        return ICommunityAnnotable.providedBy(profile)
        