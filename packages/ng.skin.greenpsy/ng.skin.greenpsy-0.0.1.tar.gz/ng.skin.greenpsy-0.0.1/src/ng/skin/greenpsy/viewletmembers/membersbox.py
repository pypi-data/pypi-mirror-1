### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last registered members

$Id: membersbox.py 51366 2008-07-14 16:53:01Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51366 $"


from ng.skin.base.viewlet.viewletmain.mainbox  import MainBox

class MembersBox(MainBox) :
    """ List of last registered members
    """
    foldername = "profile"