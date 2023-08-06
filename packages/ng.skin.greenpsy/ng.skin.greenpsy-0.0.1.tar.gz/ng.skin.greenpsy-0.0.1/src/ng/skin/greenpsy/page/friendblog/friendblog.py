### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FriendBlog class for the Zope 3 based ng.skin.greenpsy package

$Id: friendblog.py 51736 2008-09-16 20:53:35Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51736 $"

from ng.site.content.profileadapter.profileadapter import profileadapter
from ng.content.annotation.friendobjectqueueannotation.interfaces import IFriendObjectQueueAnnotation

class FriendBlog(object) :

    @property
    def friendlist(self) :
        foqa = IFriendObjectQueueAnnotation(self.context)
        if self.context == profileadapter(self.context,self.request) :
            foqa.count = 0     
        return foqa
        
        