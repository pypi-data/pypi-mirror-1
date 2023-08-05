############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
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
# FILE: profiler.py                                                        #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
# This collection of functions handle user profiles for the editor.        #
# It provides support for customization of settings and preferences to be  #
# saved in between sessions.                                               #
#                                                                          #
# SPECIFICATIONS:                                                          #
# The format of the profile file is                                        #
#                                                                          #
# LABLE [<TAB(S)> or <SPACE(S)>] VALUE                                     #
#                                                                          #
# Comment lines are denoted by a '#' mark.                                 #
#                                                                          #
# Only one value can be set per line all other statements                  #
# after the first one will be ignored.                                     #
#                                                                          #
# EOF marks the end of file, no configuration data will be read past       #
# this keyword.                                                            #
#                                                                          #
#   LABLES              VALUES                                             #
# ----------------------------------------                                 #
#  MODE	                CODE, DEBUG                                        #
#  THEME                DEFAULT                                            #
#  ICONS                Default, Nuovo, ect...                             #
#  LANG	                ENGLISH, JAPANESE                                  #
#  WRAP                 On, Off, True, False	                           #
#  SYNTAX               On, Off, True, False                               #
#  GUIDES               On, Off, True, False	                           #
#  KWHELPER             On, Off, True, False	                           #
#  TOOLBAR              On, Off, True, False	                           #
#  LASTFILE             path/to/file                                       #
#                                                                          #
# METHODS:                                                                 #
# ReadProfile: Reads a profile into the profile dictionary                 #
# WriteProfile: Writes a profile dictionary to a file	                   #
# LoadProfile: Checks loader for last used profile	                       #
# UpdateProfileLoader: Updates loader after changes to profile	           #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: profiler.py 267 2007-07-07 10:38:04Z CodyPrecord $"
__revision__ = "$Revision: 267 $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
from ed_glob import CONFIG, PROFILE, prog_name, version
import util
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

#---- Begin Function Definitions ----#
def AddFileHistoryToProfile(file_history):
    """Manages work of adding a file from the profile in order
    to allow the top files from the history to be available 
    the next time the user opens the program.
    @param file_history: add saved files to history list

    """
    size = file_history.GetNoHistoryFiles()
    file_key = "FILE"
    i = 0

    while size > i:
        key = file_key + str(i)
        file_path = file_history.GetHistoryFile(i)
        PROFILE[key] = file_path
        i += 1
    return i

def CalcVersionValue(ver_str="0.0.0"):
    """Calculates a version value from the provided dot-formated string

    1) SPECIFICATION: Version value calculation AA.BBB.CCC
         - major values: < 1     (i.e 0.0.85 = 0.850)
         - minor values: 1 - 999 (i.e 0.1.85 = 1.850)
         - micro values: >= 1000 (i.e 1.1.85 = 1001.850)

    """
    ver_lvl = ver_str.split(u".")
    if len(ver_lvl) < 3:
        return 0
    major = int(ver_lvl[0]) * 1000
    minor = int(ver_lvl[1])
    if len(ver_lvl[2]) <= 2:
        ver_lvl[2] += u'0'
    micro = float(ver_lvl[2]) / 1000
    return float(major) + float(minor) + micro

def GetLoader():
    """Finds the loader to use"""
    user_home = wx.GetHomeDir() + util.GetPathChar()
    rel_prof_path = ("." + prog_name + util.GetPathChar() + 
                     "profiles" + util.GetPathChar() + ".loader")

    if os.path.exists(user_home + rel_prof_path):
        loader = user_home + rel_prof_path
    else:
        loader = CONFIG['PROFILE_DIR'] + ".loader"

    return loader

def GetProfileStr():
    """Reads the profile string from the loader and returns it.
    The profile string must be the first line in the loader file.
    @return: path of profile used in last session

    """
    reader = util.GetFileReader(GetLoader())
    if reader == -1:
        dev_tool.DEBUGP("[profiler] [exception] Failed to open profile loader")
        # So return the default
        dev_tool.DEBUGP("[prof_info] Trying Default Profile")
        return CONFIG['PROFILE_DIR'] + u"default.pp"

    profile = reader.readline()
    profile = profile.split("\n")[0] # strip newline from end
    reader.close()
    return profile

def LoadProfile():
    """Loads Last Used Profile
    @return: whether load was succesfull or not

    """
    profile = GetProfileStr()
    if profile == "":
        profile = "default.pp"

    if os.path.isabs(profile):
        retval = ReadProfile(profile)
    else:
        retval = ReadProfile(CONFIG['PROFILE_DIR'] + profile)
    return retval

def ProfileIsCurrent():
    """Checks if profile is compatible with current editor version
    and returns a bool stating if it is or not.
    @return: whether profile on disk was written with current program version

    """
    if CalcVersionValue(ProfileVersionStr()) >= CalcVersionValue(version):
        return True
    else:
        return False

def ProfileVersionStr():
    """Checks the Loader for the profile version string and
    returns the version string. If there is an error or the
    string is not found it returns a zero version string.
    @return: the version string value from the profile loader file

    """
    loader = GetLoader()
    reader = util.GetFileReader(loader)
    if reader == -1:
        dev_tool.DEBUGP('[profile] [exception] Failed to open loader')
        return "0.0.0"

    ret_val = "0.0.0"
    count = 0
    while True:
        count += 1
        value = reader.readline()
        value = value.split()
        if len(value) > 0:
            if value[0] == u'VERSION':
                ret_val = value[1]
                break
        # Give up after 20 lines if version string not found
        if count > 20:
            break
    reader.close()

    return ret_val

def ReadProfile(profile):
    """Reads profile settings from a file into the
    profile dictionary.
    @postcondition: profile is loaded into memory from disk
    @see: ed_glob.PROFILE
    @todo: Should do value validation and default to ed_glob on invalid
           values, to prevent errors from improperly editted profiles.

    """
    reader = util.GetFileReader(profile)
    if reader == -1:
        dev_tool.DEBUGP("[profiler] [exception] Loading Profile: " + profile +
                        "\n[prof_warn] Loaded Default Profile Settings")
        PROFILE['MYPROFILE'] = os.path.join(os.path.split(profile)[0], 
                                            u"default.pp")
        return 1

    conv = unicode
    if isinstance(reader, file):
        conv = str

    lable = ""
    val = ""
    values = []
    invalid_line = 0

    # Parse File
    lines = reader.readlines()
    for line in lines:
        if line != "" and line[0] != "#":
            values = line.split()

            # Populate Profile Dictionary
            if len(values) >= 2:
                lable = values[0]
                val = " ".join(values[1:])

                # Convert int values from string to int
                if val.isdigit():
                    val = int(val)

                # If val is a bool convert it from string
                if val in [conv("True"), conv("On")]:
                    val = True
                elif val in [conv("False"), conv("Off")]:
                    val = False
                else:
                    pass

                if lable in [conv('WSIZE'), conv('WPOS'), conv('ICON_SZ')]:
                    val = util.StrToTuple(val)

                PROFILE[lable] = val
        else:
            invalid_line += 1

    # Save this profile as my profile
    PROFILE['MYPROFILE'] = profile
    reader.close()
    dev_tool.DEBUGP("[prof_info] Loaded Profile: " + profile)
    return 0

def UpdateProfileLoader():
    """Updates Loader File
    @postcondition: on disk profile loader is updated
    @return: 0 if no error, non zero for error condition

    """
    writer = util.GetFileWriter(GetLoader())
    if writer == -1:
        dev_tool.DEBUGP("[profiler] [exception] Failed to open "
                        "profile loader for writting")
        return 1

    if isinstance(writer, file):
        conv = str
    else:
        conv = unicode

    writer.write(conv(PROFILE['MYPROFILE']))
    writer.write(u"\nVERSION\t" + version)
    writer.close()
    return 0

def WriteProfile(profile):
    """Writes a profile to a file
    @postcondition: profile is saved to disk.

    """
    writer = util.GetFileWriter(profile)
    if writer == -1:
        return -1

    if isinstance(writer, file):
        conv = str
    else:
        conv = unicode
    header = u"# " + profile + u"\n# Editra " + version + u" Profile\n" \
              + u"# You are can edit this file but be aware that if it\n" \
              + u"# is your active profile it will be overwritten the next\n" \
              + u"# time you close the editor.\n" \
              + u"#\n# Lable\t\t\tValue #" + \
              u"\n#-----------------------------#\n"

    writer.write(header)

    prof_keys = PROFILE.keys()
    prof_keys.sort()

    if not PROFILE['SET_WSIZE']:
        if 'WSIZE' in prof_keys:
            prof_keys.remove('WSIZE')
    if not PROFILE['SET_WPOS']:
        if 'WPOS' in prof_keys:
            prof_keys.remove('WPOS')

    for item in prof_keys:
        writer.write(conv(item) + u"\t\t" + conv(PROFILE[item]) + u"\n")

    writer.write(u"\n\nEOF\n")
    dev_tool.DEBUGP("[prof_info] Wrote out Profile: " + profile)

    PROFILE['MYPROFILE'] = profile
    writer.close()
    return 0
