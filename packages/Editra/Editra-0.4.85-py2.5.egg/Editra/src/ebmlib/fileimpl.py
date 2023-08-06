###############################################################################
# Name: Cody Precord                                                          #
# Purpose: File Object Interface Implementation                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Buisness Model Library: FileObjectImpl

Implementation of a file object interface class. Objects and methods inside
of this library expect a file object that derives from this interface.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: fileimpl.py 60326 2009-04-25 00:57:22Z CJP $"
__revision__ = "$Revision: 60326 $"

#--------------------------------------------------------------------------#
# Imports

#--------------------------------------------------------------------------#

class FileObjectImpl(object):
    """File Object Interface implementation base class"""
    def __init__(self):
        object.__init__(self)

    
