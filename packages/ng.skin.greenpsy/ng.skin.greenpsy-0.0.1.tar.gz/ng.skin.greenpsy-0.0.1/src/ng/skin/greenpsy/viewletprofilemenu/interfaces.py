### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 51314 2008-07-09 10:06:22Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51314 $"
 
from zope.interface import Interface

class IProfileMenuBoxProvider(Interface) :
    """ Interface for ProfileMenuBox provider
    """
