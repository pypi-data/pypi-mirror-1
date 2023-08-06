### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51521 2008-08-25 08:08:01Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51379 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Text, Date


class IRegisterForm(Interface) :
    """ """

    title = TextLine(title=u'FullName',
                    description=u'Your full name',
                    required=True,
                    default=u'',
                   )

    nickname = TextLine(title=u'Nickname',
                    description=u'Your nickname',
                    required=True,
                    default=u'',
                   )

    birthday = Date(title=u'Birthday',
                    description=u'Your Birth Day',
                    required=True,
                    default=None,
                   )

    abstract = Text(title=u'About',
                    description=u'You can write a few words about yourself',
                    required=False,
                    default=u'',
                   )
