############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#			                                    						   #
#    Editra is free software; you can redistribute it and#or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: autocomp.py                                                        #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#    Provides an interface/service for getting autocompletion/calltip data #
# into an stc control. This is a data provider only it does not do provide #
# any UI functionality or calls. The user called object from this library  #
# is intended to be the AutoCompService. This service provides the generic #
# interface into the various language specific autocomplete services, and  #
# makes the calls to the other support objects/functions in this library.  #
#                                                                          #
# METHODS:                                                                 #
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: autocomp.py 248 2007-06-26 12:44:31Z CodyPrecord $"
__revision__ = "$Revision: 248 $"

#--------------------------------------------------------------------------#
# Dependancies
import wx.stc as stc
#--------------------------------------------------------------------------#

class AutoCompService(object):
    """Interface to retrieve and provide autcompletion and
    calltip information to an stc control. The plain text
    (empty) completion provider is built in. All other provders
    are loaded from external modules on request.

    """
    def __init__(self, parent):
        """Initializes the autocompletion service
        @param parent: parent of this service object

        """
        object.__init__(self)
        self._buffer = parent
        self._completer = None

    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the
        autocompletion.
        @return: list of characters used for activating autocomp

        """
        if self._completer != None:
            return self._completer.GetAutoCompKeys()
        else:
            return list()

    def GetAutoCompList(self, command, namespace = None):
        """Retrieves the sorted autocomplete list for a command
        @param command: command string to do lookup on
        @keyword namespace: namespace to use

        """
        if self._completer != None:
            return self._completer.GetAutoCompList(command, namespace)
        else:
            return list()
 
    def GetAutoCompStops(self):
        """Returns a string of characters that should cancel
        the autocompletion lookup.
        @return: string of characters that will hide the autocomp/calltip

        """
        if self._completer != None:
            return self._completer.GetAutoCompStops()
        else:
            return u''

    def GetCallTip(self, command, namespace = None):
        """Returns the calltip string for a command
        @param command: command to get callip for
        @keyword namespace: namespace to do lookup in

        """
        if self._completer != None:
            return self._completer.GetCallTip(command, namespace)
        else:
            return u''

    def GetCallTipKeys(self):
        """Returns the list of keys to activate a calltip on
        @return: list of calltip activation keys

        """
        if self._completer != None:
            return self._completer.GetCallTipKeys()
        else:
            return list()

    def GetIgnoreCase(self):
        """Are commands case sensitive or not
        @return: whether case is ignored or not by lookup

        """
        if self._completer != None:
            return not self._completer.GetCaseSensitive()
        else:
            return True

    def LoadCompProvider(self, lex_value):
        """Loads a specified completion provider by stc_lex value
        @param lex_value: lexer id to get autocomp service for

        """
        if lex_value == stc.STC_LEX_PYTHON:
            import pycomp
            self._completer = pycomp.Completer(self._buffer)
        else:
            pass

    def UpdateNamespace(self, opt = None):
        """Tells the completer to update its namespace
        @keyword opt: specific option to pass to completer for updating the
                      namespace.

        """
        if self._completer != None and hasattr(self._completer, \
                                               'UpdateNamespace'):
            if opt == None:
                self._completer.UpdateNamespace()
            else:
                self._completer.UpdateNamespace(opt)
        else:
            pass
