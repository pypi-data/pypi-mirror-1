# -*- coding: utf-8 -*-
"""Interface definition used to display form of community selection

$Id: interfaces.py 51777 2008-09-24 20:04:46Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51777 $"


from zope.interface import Interface
from zope.schema import Choice

class ICommunityChoice(Interface) :
    
    cid = Choice(
            title=u"Community",
            vocabulary = "mycommunityvocabulary",
            required=False
            )