### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for content viewlet

$Id: blog.py 51372 2008-07-15 12:26:48Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from ng.skin.base.page.contentlet.viewletbase import ViewletBase
from ng.app.objectqueue.interfaces import IObjectQueue

class Blog(ViewletBase) :
    """ Content """

    @property
    def values(self) :
        return IObjectQueue(self.context).values()