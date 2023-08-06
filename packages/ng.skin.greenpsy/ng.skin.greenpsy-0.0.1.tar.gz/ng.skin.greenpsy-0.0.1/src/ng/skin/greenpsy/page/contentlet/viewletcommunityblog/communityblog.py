### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for content viewlet

$Id: communityblog.py 51777 2008-09-24 20:04:46Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from ng.skin.base.page.contentlet.viewletbase import ViewletBase
from ng.content.annotation.communityobjectqueueannotation.interfaces import ICommunityObjectQueueAnnotation

class CommunityBlog(ViewletBase) :
    """ Content """

    @property
    def articles(self) :
        return ICommunityObjectQueueAnnotation(self.context)
