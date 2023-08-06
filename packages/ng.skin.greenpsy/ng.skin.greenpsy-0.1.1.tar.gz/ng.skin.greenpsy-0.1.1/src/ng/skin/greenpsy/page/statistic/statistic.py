### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Statistic class for the Zope 3 based ng.skin.greenpsy package

$Id: statistic.py 52412 2009-01-30 11:52:27Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52412 $"


from ng.site.addon.profile.profileadapter.profileadapter import profileadapter
from ng.content.profile.friendshipannotation.interfaces import IFriendshipAnnotation, IFriend
from ng.content.profile.friendobjectqueueannotation.interfaces import IFriendObjectQueueAnnotation
from ng.content.profile.exchangeannotation.interfaces import IExchangeAnnotation, IExchangeContainer
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from ng.content.article.division.interfaces import IDivision


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
        

    @property
    def friendsWithMessages(self) :
        f = IFriendshipAnnotation(profileadapter(self.context,self.request)).friends()
        profile = IExchangeAnnotation(profileadapter(self.context,self.request))
        fwm = []
        
        for i in f:
            pid = unicode(IFriend(i).id)
            try:
                if IExchangeContainer(profile[pid]).count != 0:
                    fwm.append({u'count':IExchangeContainer(profile[pid]).count,
                                u'title':IDivision(IFriend(i).profile).title,
                                u'url':adaptiveURL(IFriend(i).profile, self.request) + u'/@@chat.html'})
            ### TODO убедиться, что это нужный эксепшен
            except KeyError:
                pass
        return fwm
