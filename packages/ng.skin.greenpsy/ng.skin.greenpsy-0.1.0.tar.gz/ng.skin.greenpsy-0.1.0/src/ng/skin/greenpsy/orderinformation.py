### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: orderinformation.py 52495 2009-02-09 23:30:26Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52495 $"

from ng.lib.orderinformation import OrderInformation

class ContentOrderInformation(OrderInformation) :
    name = ["abstract", "body", "photo",   "backref",  "contenticons", "reference",  "comment", "content" ]

class LeftColumnOrderInformation(OrderInformation) :
    name = [ "rubriccloud", "currentbox", "rubriclist", "fastsearchbox", "topcommunitiesbox", "membersbox", "subscribe",  ]
    
class RightColumnOrderInformation(OrderInformation) :
    name = [ "googleadsbox", "toolbox", "loginbox", "newslistbox" ]
