### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for content viewlet

$Id: communityblog.py 52243 2008-12-29 00:28:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from ng.lib.viewletbase import ViewletBase
from ng.content.profile.communityobjectqueueannotation.interfaces import ICommunityObjectQueueAnnotation

class CommunityBlog(ViewletBase) :
    """ Content """

    @property
    def articles(self) :
        return ICommunityObjectQueueAnnotation(self.context)
