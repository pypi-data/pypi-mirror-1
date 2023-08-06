### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 51310 2008-07-09 04:29:09Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51310 $"
 
from zope.interface import Interface

class IFastSearchBoxProvider(Interface) :
    """ Interface for FastSearchBox provider
    """
