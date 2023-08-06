### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for photosequence adding page

$Id: addcommunity.py 51785 2008-09-25 09:31:02Z cray $
"""
__author__  = u"Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51785 $"

from zope.interface import implements
from zope.schema import getFieldNames

from ng.content.article.interfaces import IDocShort 
from zope.app.zapi import absoluteURL, getUtility
from zope.app.container.interfaces import INameChooser, IContainer
from ng.site.content.communityfactory.community import CommunityCreate 

class AddCommunity(object) :
    def getData(self,*kv,**kw) :
        return [ (x,IDocShort[x].default) for x in getFieldNames(IDocShort) ]
        
    def setData(self,d,**kw) :
        division = getUtility(IContainer,context=self.context,name='community')
        community = CommunityCreate(self.request.principal.id)
        print d

        community.title = d['title']
                
        division[INameChooser(division).chooseName(d['title'],community)] = community

        for key in getFieldNames(IDocShort) :
            setattr(community,key,d[key])

        self.request.response.redirect(absoluteURL(community,self.request))        
        return u"Зашибись"