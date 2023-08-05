###############################################################################
#    Copyright (C) 2007 Editra Development Team                               #
#    staff@editra.org                                                         #
#                                                                             #
#    This program is free software; you can redistribute it and#or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
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
# FILE: ruby.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Ruby.                                        #
#                                                                             #
# @todo: Default Style Refinement.                                            #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ruby.py 268 2007-07-07 14:37:37Z CodyPrecord $"
__revision__ = "$Revision: 268 $"

#-----------------------------------------------------------------------------#
# Dependancies

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Ruby Keywords
RUBY_KW = (0, "__FILE__ and def end in or self unless __LINE__ begin defined? "
              "ensure module redo super until BEGIN break do false next rescue "
              "then when END case else for nil retry true while alias class "
              "elsif if not return undef yieldr puts")

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [ ('STC_RB_BACKTICKS', 'scalar_style'),
                 ('STC_RB_CHARACTER', 'char_style'),
                 ('STC_RB_CLASSNAME', 'class_style'),
                 ('STC_RB_CLASS_VAR', 'default_style'), # STYLE ME
                 ('STC_RB_COMMENTLINE', 'comment_style'),
                 ('STC_RB_DATASECTION', 'default_style'), # STYLE ME
                 ('STC_RB_DEFAULT', 'default_style'),
                 ('STC_RB_DEFNAME', 'keyword3_style'), # STYLE ME
                 ('STC_RB_ERROR', 'error_style'),
                 ('STC_RB_GLOBAL', 'global_style'),
                 ('STC_RB_HERE_DELIM', 'default_style'), # STYLE ME
                 ('STC_RB_HERE_Q', 'here_style'), 
                 ('STC_RB_HERE_QQ', 'here_style'),
                 ('STC_RB_HERE_QX', 'here_style'),
                 ('STC_RB_IDENTIFIER', 'default_style'),
                 ('STC_RB_INSTANCE_VAR', 'scalar2_style'),
                 ('STC_RB_MODULE_NAME', 'global_style'), # STYLE ME
                 ('STC_RB_NUMBER', 'number_style'),
                 ('STC_RB_OPERATOR', 'operator_style'),
                 ('STC_RB_POD', 'default_style'), # STYLE ME
                 ('STC_RB_REGEX', 'regex_style'), # STYLE ME
                 ('STC_RB_STDIN', 'default_style'), # STYLE ME
                 ('STC_RB_STDOUT', 'default_style'), # STYLE ME
                 ('STC_RB_STRING', 'string_style'),
                 ('STC_RB_STRING_Q', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QQ', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QR', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QW', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QX', 'default_style'), # STYLE ME
                 ('STC_RB_SYMBOL', 'default_style'), # STYLE ME
                 ('STC_RB_UPPER_BOUND', 'default_style'), # STYLE ME
                 ('STC_RB_WORD', 'keyword_style'),
                 ('STC_RB_WORD_DEMOTED', 'keyword2_style') ]

#---- Extra Properties ----#
FOLD = ("fold", "1")
TIMMY = ("fold.timmy.whinge.level", "1")
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return [RUBY_KW]

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return SYNTAX_ITEMS

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [FOLD, TIMMY]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return [u'#']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return RUBY_KW[1]

#---- End Syntax Modules Internal Functions ----#
