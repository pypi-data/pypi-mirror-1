### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for redirect page.

$Id: searchpage.py 52472 2009-02-08 00:08:16Z cray $



"""
__author__  = "Andrey Orlov 2009"
__license__ = "GPL"
__version__ = "$Revision: 52472 $"

import zope.component
from ng.content.annotation.redirectannotation.interfaces import IRedirectAnnotation

class Redirect(object) :
    def __call__(self) :
        self.request.response.redirect(IRedirectAnnotation(self.context).redirect)
        return ""
