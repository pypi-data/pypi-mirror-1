###############################################################################
# Name: common.py                                                             #
# Purpose: Common utilities for unittests.                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: common.py 59007 2009-02-18 21:56:40Z CJP $"
__revision__ = "$Revision: 59007 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

#-----------------------------------------------------------------------------#

class EdApp(wx.App):
    def GetLog(self):
        return lambda msg: None
