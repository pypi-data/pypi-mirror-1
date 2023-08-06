### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for abstract viewlet for profile

$Id: profileabstract.py 51385 2008-07-16 10:02:09Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.skin.base.page.contentlet.viewletbase import ViewletBase
from ng.content.annotation.profileannotation.interfaces import IProfileAnnotation

class Proxy(object) :
    def __init__(self,ob) :
        self.ob = ob
        self.ps = IPropertySheet(ob)
        self.profile = IProfileAnnotation(ob)
                        
    @property
    def abstract(self) :
        return self.ps['abstract'] or self.ps.get('auto',u"")
        
    @property
    def title(self) :
        return self.ps['title'] or self.ob.__name__
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)

class ProfileAbstract(ViewletBase) :
    """ Abstract """

    def __init__(self,*kv,**kw) :
        super(ProfileAbstract,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
        