# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 52489 2009-02-09 12:51:27Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52489 $"

from ng.skin.base.interfaces import AuthSkin,RubricatorSkin, CommunitySkin,CommentSkin,BaseSkin
from zope.app.rotterdam import Rotterdam

class GreenpsySkin(AuthSkin,RubricatorSkin,CommunitySkin,CommentSkin,BaseSkin,Rotterdam) : 
    """Skin for for GreenPsy"""