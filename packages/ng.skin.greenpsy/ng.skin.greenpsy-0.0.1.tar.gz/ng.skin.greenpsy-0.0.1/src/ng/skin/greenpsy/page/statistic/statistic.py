### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Statistic class for the Zope 3 based ng.skin.greenpsy package

$Id: statistic.py 51733 2008-09-16 20:33:58Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51733 $"


from ng.site.content.profileadapter.profileadapter import profileadapter
from ng.content.annotation.friendshipannotation.interfaces import IFriendshipAnnotation
from ng.content.annotation.friendobjectqueueannotation.interfaces import IFriendObjectQueueAnnotation
from ng.content.profile.exchangeannotation.interfaces import IExchangeAnnotation

class Statistic(object) :

    @property
    def suggestlength(self) :
        return IFriendshipAnnotation(profileadapter(self.context,self.request)).suggestslength
                                                  
    @property
    def messagelength(self) :
        return IExchangeAnnotation(profileadapter(self.context,self.request)).count
        
    @property
    def friendlistlength(self) :
        return IFriendObjectQueueAnnotation(profileadapter(self.context,self.request)).count 
        
        