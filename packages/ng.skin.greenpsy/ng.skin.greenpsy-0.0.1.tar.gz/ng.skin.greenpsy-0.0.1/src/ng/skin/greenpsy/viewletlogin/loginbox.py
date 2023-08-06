### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with login box

$Id: loginbox.py 51408 2008-07-18 10:40:31Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51408 $"


class LoginBox(object) :
    """ Login box
    """
#    def __init__(self,*kv,**kw) :
#        super(LoginBox,self).__init__(*kv,**kw)
    def check(self) :
        print "CHECK PRINCIPAL"
        print "PRINCIPAL", self.request.principal
        if "zope.Authenticated" in self.request.principal.groups :
            raise ValueError
            