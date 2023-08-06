### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 51850 2008-10-16 20:44:00Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51850 $"
 
from zope.interface import Interface

class IRubricListProvider(Interface) :
    """ Interface for RubricList provider
    """
