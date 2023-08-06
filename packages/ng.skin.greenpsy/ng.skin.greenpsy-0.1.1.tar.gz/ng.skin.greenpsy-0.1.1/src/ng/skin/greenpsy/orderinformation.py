### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: orderinformation.py 52646 2009-02-16 23:38:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52646 $"

from ng.lib.orderinformation import OrderInformation

class ContentOrderInformation(OrderInformation) :
    name = ["abstract", "body", "photo",   "backref",  "contenticons", "reference",  "comment", "content" ]

class LeftColumnOrderInformation(OrderInformation) :
    name = [ "rubriccloud", "currentbox", "rubriclist", "fastsearchbox", "topcommunitiesbox", "membersbox", "subscribe",  ]
    
class RightColumnOrderInformation(OrderInformation) :
    name = [ "googleadsbox", "loginbox", "toolbox",  "newslistbox" ]
