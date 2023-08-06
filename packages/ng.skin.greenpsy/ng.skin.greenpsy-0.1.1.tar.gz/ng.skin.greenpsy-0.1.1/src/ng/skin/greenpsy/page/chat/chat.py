### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Chat class for the Zope 3 based ng.skin.greenpsy package

$Id: chat.py 52412 2009-01-30 11:52:27Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52412 $"

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from ng.content.profile.exchangeannotation.interfaces import IExchangeAnnotation, IMailboxContainer, IMessage
from ng.content.profile.exchangeannotation.exchange import Exchange
from ng.content.profile.exchangeannotation.message import Message
from ng.content.profile.friendshipannotation.interfaces import IFriendshipAnnotation
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from zope.security.proxy import removeSecurityProxy
from ng.site.addon.profile.profileadapter.profileadapter import profileadapter

class Chat(object) :

    page = ViewPageTemplateFile("chat.pt")
    #pageedit = ViewPageTemplateFile("friendlistedit.pt")
    
    
    @property
    def checkpermission(self) :
        return IFriendshipAnnotation(self.context).check(profileadapter(self.context,self.request))


    @property
    def profileid(self) :
        for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( self.request.principal.id, self.request.principal.id )
                          ) :
            return unicode(getUtility(IIntIds,context=self.context).getId(profile))

    @property
    def exchanger_self(self) :
        for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( self.request.principal.id, self.request.principal.id )
                          ) :
           
            mailbox = IMailboxContainer(IExchangeAnnotation(profile))
            profileid = unicode(getUtility(IIntIds,context=self.context).getId(self.context))

            try :
                exchange = mailbox[profileid]
            except KeyError :
                exchange = mailbox[profileid] = Exchange()

            return exchange                
    
    def send(self, *kv, **kw) :
        for exchanger in [self.exchanger_self] : 
            message = exchanger.add(Message())
            IMessage(message).abstract = unicode(self.request.form['abstract'])
            IMessage(message).author = self.request.principal.id
        
        message = Message()
        IMessage(message).abstract = unicode(self.request.form['abstract'])
        IMessage(message).author = self.request.principal.id
            
        IExchangeAnnotation(self.context).add(self.profileid,message)

        return self.page(self,message=u'Send message', *kv, **kw)
        
    def update(self,*kv, **kw) :
        return self.page(self,message=u'', *kv, **kw)

    def reset(self) :
        self.exchanger_self.count = 0

    def messages(self) :
        self.exchanger_self.count = 0
        return self.exchanger_self #.values()
                
   
