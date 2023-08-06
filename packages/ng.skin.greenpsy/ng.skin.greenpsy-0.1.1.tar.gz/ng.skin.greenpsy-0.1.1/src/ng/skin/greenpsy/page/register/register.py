### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mixin class for specific register form

$Id: register.py 52188 2008-12-25 20:27:05Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50628 $"

from zope.app.zapi import getUtility
from zope.schema import getFieldNames
from ng.content.article.interfaces import IDocShort
from ng.content.profile.profileannotation.interfaces import IProfileAnnotation
from interfaces import IRegisterForm

class Register(object) :
    interfaces = [IProfileAnnotation, IDocShort]

    def getData(self,*kv,**kw) :
        for name in getFieldNames(IRegisterForm) :
            for interface in self.interfaces :
                if name in interface :
                    yield (name,getattr(interface(self.context),name))
    
        #return [ (x,getattr(util,x)) for x in  getFieldNames(IBookmarkNote)]

    def setData(self,d,**kw) :
        for name in getFieldNames(IRegisterForm) :
            for interface in self.interfaces :
                if name in interface :
                    setattr(interface(self.context),name,d[name])

        return u"Registration info updated"
