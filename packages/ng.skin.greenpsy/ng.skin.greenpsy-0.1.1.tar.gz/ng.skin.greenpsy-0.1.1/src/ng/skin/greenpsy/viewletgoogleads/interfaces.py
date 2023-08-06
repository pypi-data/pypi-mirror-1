### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 51327 2008-07-10 05:35:13Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51327 $"
 
from zope.interface import Interface

class IGoogleAdsBoxProvider(Interface) :
    """ Interface for GoogleAdsBox provider
    """
