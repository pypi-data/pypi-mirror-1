### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for photosequence adding page

$Id: communitychoice.py 51781 2008-09-24 21:19:51Z cray $
"""
__author__  = u"Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51781 $"

from zope.interface import implements
from zope.schema import getFieldNames

from interfaces import ICommunityChoice
from zope.app.zapi import absoluteURL, getUtility
from ng.content.annotation.communityobjectqueueannotation.interfaces import ICommunityObjectQueueAnnotation
from zope.app.intid.interfaces import IIntIds

class CommunityChoice(object) :
    def getData(self,*kv,**kw) :
        return [ (x,u"") for x in getFieldNames(ICommunityChoice) ]
        
    def setData(self,d,**kw) :
        cid = d['cid']
        print cid
        community = getUtility(IIntIds,context = self.context).getObject(cid)
        ICommunityObjectQueueAnnotation(community).handleModified(self.context)
        self.request.response.redirect(absoluteURL(community,self.request))        
        return u"Зашибись"