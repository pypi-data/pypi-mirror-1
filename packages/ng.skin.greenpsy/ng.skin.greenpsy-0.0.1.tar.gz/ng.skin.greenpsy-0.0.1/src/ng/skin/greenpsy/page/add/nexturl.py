### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for add form to redirect on @@commonedit.html

$Id: nexturl.py 51447 2008-07-29 08:00:46Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.traversing.browser.absoluteurl import absoluteURL

class NextUrl(object) :
    """ Content """

    def create(self, *args, **kw):
       """Do the actual instantiation."""
       self.ob = self._factory(*args, **kw)
       print "--------->",self.ob
       return self.ob
                   

    def nextURL(self):
        print "abs:",absoluteURL(self.ob,self.request)
        return absoluteURL(self.ob,self.request) + "/@@commonedit.html" 
            
            