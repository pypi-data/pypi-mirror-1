### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 51308 2008-07-09 03:23:20Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51308 $"
 
from zope.interface import Interface

class IMembersBoxProvider(Interface) :
    """ Interface for MembersBox provider
    """
