### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 51329 2008-07-10 06:00:57Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51329 $"
 
from zope.interface import Interface

class ILoginBoxProvider(Interface) :
    """ Interface for LoginBox provider
    """
