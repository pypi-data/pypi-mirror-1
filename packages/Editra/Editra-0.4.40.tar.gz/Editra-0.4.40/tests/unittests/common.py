###############################################################################
# Name: common.py                                                             #
# Purpose: Common utilities for unittests.                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: common.py 57492 2008-12-22 00:48:12Z CJP $"
__revision__ = "$Revision: 57492 $"

#-----------------------------------------------------------------------------#
# Importsimport wx

#-----------------------------------------------------------------------------#

class EdApp(wx.App):
    def GetLog(self):
        return lambda msg: None
