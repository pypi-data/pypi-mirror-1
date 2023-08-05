#----------------------------------------------------------------------------
# Name:         ColourSelect.py
# Purpose:      Colour Box Selection Control
#
# Author:       Lorne White, Lorne.White@telusplanet.net
#
# Created:      Feb 25, 2001
# Licence:      wxWindows license
#----------------------------------------------------------------------------

# creates a colour wxButton with selectable color
# button click provides a colour selection box
# button colour will change to new colour
# GetColour method to get the selected colour

# Updates:
# 07/16/2007 Cody Precord, <codyprecord@gmail.com>
# - SetLabel now actually changes the label drawn in the button when called
# - Fixed a bug with the button display for the new SetBitmapHover state on msw
# - Added docstrings to most of the objects
# - Cleaned up some minor coding convention issues

# call back to function if changes made

# Cliff Wells, logiplexsoftware@earthlink.net:
# - Made ColourSelect into "is a button" rather than "has a button"
# - Added label parameter and logic to adjust the label colour according to the 
#   background colour
# - Added id argument
# - Rearranged arguments to more closely follow wx conventions
# - Simplified some of the code

# Cliff Wells, 2002/02/07
# - Added ColourSelect Event

# 12/01/2003 - Jeff Grimmett (grimmtooth@softhome.net)
#
# o Updated for 2.5 compatability.
#

"""
Provides a `ColourSelect` button that, when clicked, will display a
colour selection dialog.  The selected colour is displayed on the
button itself.
"""

#----------------------------------------------------------------------------

import  wx

#----------------------------------------------------------------------------

wxEVT_COMMAND_COLOURSELECT = wx.NewEventType()

class ColourSelectEvent(wx.PyCommandEvent):
    def __init__(self, id, value):
        wx.PyCommandEvent.__init__(self, id=id)
        self.SetEventType(wxEVT_COMMAND_COLOURSELECT)
        self.value = value

    def GetValue(self):
        """Gets the value of the selected color as a wx.Colour object"""
        return self.value

EVT_COLOURSELECT = wx.PyEventBinder(wxEVT_COMMAND_COLOURSELECT, 1)

#----------------------------------------------------------------------------

class ColourSelect(wx.BitmapButton):
    """Create and show a button with a colour background and optional
    label. Clicking on the button will open a L{wx.ColourDialog}.

    """
    def __init__(self, parent, id=wx.ID_ANY, label=wx.EmptyString, 
                 colour=wx.BLACK, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 callback=None, style=0):
        """Default class constructor
        
        All parameters are as in wxPython L{wxBitmapButton} class constructor 
        except the following two keywords:
        @keyword colour: (R, G, B) Tuple or wx.Colour to initialize button with
        @keyword callback: Callback function to call after colour changes

        """
        if label:
            w, h = parent.GetTextExtent(label)
            w += 6
            h += 6
        else:
            w, h = 20, 20
        wx.BitmapButton.__init__(self, parent, id, wx.EmptyBitmap(w, h),
                                 pos=pos, size=size, 
                                 style=style | wx.BU_AUTODRAW)

        if type(colour) == tuple:
            colour = wx.Colour(*colour)

        # Attributes
        self.colour = colour
        self.label = label
        self.callback = callback

        # Create Buttons Bitmap
        self.SetBitmap(self.MakeBitmap())

        # Event Handlers
        parent.Bind(wx.EVT_BUTTON, self.OnClick, self)

    #---- Public Methods ----#
    def GetColour(self):
        """Gets the colour of the button
        @return: wx.Colour

        """
        return self.colour

    def GetValue(self):
        """Gets the colour of the button
        @return: wx.Colour

        """
        return self.colour

    def SetValue(self, colour):
        """Sets the colour value of the button
        @param colour: colour to set value to
        @type colour: (R, G, B) Tuple, named string, or wx.Colour

        """
        self.SetColour(colour)

    def SetColour(self, colour):
        """Sets the colour value of the button
        @param colour: colour to set value to
        @type colour: (R, G, B) Tuple, named string, or wx.Colour

        """
        if type(colour) == tuple:
            colour = wx.Colour(*colour)
        if type(colour) == str:
            colour = wx.NamedColour(colour)
            
        self.colour = colour
        bmp = self.MakeBitmap()
        self.SetBitmap(bmp)

    def SetLabel(self, label):
        """Sets the label of button"""
        self.label = label
        self.SetBitmap(self.MakeBitmap())

    def GetLabel(self):
        """Get the label string of the button"""
        return self.label

    def MakeBitmap(self):
        """Creates a bitmap from the ColourSelect's current colour
        and label values.
        @return: wx.Bitmap

        """
        bdr = 8
        width, height = self.GetSize()
            
        bmp = wx.EmptyBitmap(width - bdr, height - bdr)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetFont(self.GetFont())
        label = self.GetLabel()
        # Just make a little colored bitmap
        dc.SetBackground(wx.Brush(self.colour))
        dc.Clear()

        if label != wx.EmptyString:
            # Add a label to it
            avg = reduce(lambda a, b: a + b, self.colour.Get()) / 3
            fcolour = avg > 128 and wx.BLACK or wx.WHITE
            dc.SetTextForeground(fcolour)
            dc.DrawLabel(label, (0, 0, width - bdr, height - bdr),
                         wx.ALIGN_CENTER)
            
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def SetBitmap(self, bmp):
        """Sets the buttons bitmap for all states"""
        self.SetBitmapLabel(bmp)
        # On windows if the bitmap has changed since init the hover
        # state will display the bitmap from init instead of the current
        # bitmap so set the hover bitmap as well.
        if wx.Platform == '__WXMSW__' and wx.VERSION >= (2, 7, 0, 0):
            self.SetBitmapHover(bmp)
        self.Refresh()

    def OnChange(self):
        """Posts L{ColourSelectEvent} and calls the callback function
        if one was set.

        """
        wx.PostEvent(self, ColourSelectEvent(self.GetId(), self.GetValue()))
        if self.callback is not None:
            self.callback()

    def OnClick(self, event):
        """Handles EVT_BUTTON for the control by opening the
        L{wx.ColourDialog} and posting a L{ColourSelectEvent} after
        the dialog is closed.

        """
        data = wx.ColourData()
        data.SetChooseFull(True)
        data.SetColour(self.colour)
        dlg = wx.ColourDialog(wx.GetTopLevelParent(self), data)
        changed = dlg.ShowModal() == wx.ID_OK

        if changed:
            data = dlg.GetColourData()
            self.SetColour(data.GetColour())
        dlg.Destroy()

        # moved after dlg.Destroy, since who knows what the callback will do...
        if changed:
            self.OnChange() 

