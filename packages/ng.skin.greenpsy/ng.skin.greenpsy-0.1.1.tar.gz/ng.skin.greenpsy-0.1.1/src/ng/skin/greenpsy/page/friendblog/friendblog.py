### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FriendBlog class for the Zope 3 based ng.skin.greenpsy package

$Id: friendblog.py 52235 2008-12-27 22:59:22Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52235 $"

from ng.site.addon.profile.profileadapter.profileadapter import profileadapter
from ng.content.profile.friendobjectqueueannotation.interfaces import IFriendObjectQueueAnnotation

class FriendBlog(object) :

    @property
    def friendlist(self) :
        foqa = IFriendObjectQueueAnnotation(self.context)
        if self.context == profileadapter(self.context,self.request) :
            foqa.count = 0     
        return foqa
        
        