###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    staff@editra.org                                                         #
#                                                                             #
#    Editra is free software; you can redistribute it and#or modify           #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    Editra is distributed in the hope that it will be useful,                #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program; if not, write to the                            #
#    Free Software Foundation, Inc.,                                          #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                #
###############################################################################

"""
#-----------------------------------------------------------------------------#
# FILE: ada.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for ada                                          #
#                                                                             #
# @todo: styles, keywords, testing                                            #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ada.py 277 2007-07-10 10:53:45Z CodyPrecord $"
__revision__ = "$Revision: 277 $"

#-----------------------------------------------------------------------------#
import synglob
#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#
ADA_KEYWORDS = (0, "abort abstract accept access aliased all array at begin "
                    "body case constant declare delay delta digits do else "
                    "elsif end entry exception exit for function generic goto "
                    "if in is limited loop new null of others out package "
                    "pragma private procedure protected raise range record "
                    "renames requeue return reverse select separate subtype "
                    "tagged task terminate then type until use when while with")

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [('STC_ADA_CHARACTER', 'char_style'),
                 ('STC_ADA_CHARACTEREOL', 'stringeol_style'),
                 ('STC_ADA_COMMENTLINE', 'comment_style'),
                 ('STC_ADA_DEFAULT', 'default_style'),
                 ('STC_ADA_DELIMITER', 'operator_style'),
                 ('STC_ADA_IDENTIFIER', 'default_style'),
                 ('STC_ADA_ILLEGAL', 'error_style'),
                 ('STC_ADA_LABEL', 'keyword2_style'),   # Style This
                 ('STC_ADA_NUMBER', 'number_style'),
                 ('STC_ADA_STRING', 'string_style'),
                 ('STC_ADA_STRINGEOL', 'stringeol_style'),
                 ('STC_ADA_WORD', 'keyword_style')]

#---- Extra Properties ----#

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    if lang_id == synglob.ID_LANG_ADA:
        return [ADA_KEYWORDS]
    else:
        return list()

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    if lang_id == synglob.ID_LANG_ADA:
        return SYNTAX_ITEMS
    else:
        return list()

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    if lang_id == synglob.ID_LANG_ADA:
        return list()
    else:
        return list()

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    if lang_id == synglob.ID_LANG_ADA:
        return [ u'--' ]
    else:
        return list()

#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    # Unused by this module, stubbed in for consistancy
    return None

#---- End Syntax Modules Internal Functions ----#
