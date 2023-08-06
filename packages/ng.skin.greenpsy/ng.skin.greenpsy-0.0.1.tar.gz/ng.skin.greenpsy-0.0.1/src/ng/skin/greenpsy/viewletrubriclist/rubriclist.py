### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with list of rubric

$Id: rubriclist.py 51850 2008-10-16 20:44:00Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51850 $"


from zope.app.zapi import getUtility
from ng.app.link.linkbackreference.interfaces import ILinkBackReference
from zope.app.intid.interfaces import IIntIds

class RubricList(object) :
    """ List of rubric for this object
    """

    def values(self) :
        print 1
        brf = getUtility(ILinkBackReference,context=self.context)
        print 2
        intid = getUtility(IIntIds, brf.newsRefId)
        print 3
        for item in brf["c%016u" % intid.getId(self.context)] :
            print 4
            yield intid.getObject(int(item[1:])).__parent__
