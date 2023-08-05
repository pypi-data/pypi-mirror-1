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
# FILE: ed_cmdbar.py                                                       #
# @author: Cody Precord                                                    #
# LANGUAGE: Python                                                         #
# @summary:                                                                #
#    This class creates a custom panel that can hide and show different    #
# controls based an id value. The panel is generally between 24-32 pixels  #
# in height but can grow to fit the controls inserted in it. The           #
# the background is painted with a gradient using system defined colors.   #
#                                                                          #
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: ed_cmdbar.py 341 2007-08-07 23:34:03Z CodyPrecord $"
__revision__ = "$Revision: 341 $"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import util
import ed_search

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
# Close Button Bitmap
from wx import ImageFromStream, BitmapFromImage
import cStringIO, zlib

def GetXData():
    """Returns the raw image data for the close button
    @return: raw image data

    """
    return zlib.decompress(
'x\xda\x011\x02\xce\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0e\
\x00\x00\x00\x0e\x08\x02\x00\x00\x00\x90*\xba\x86\x00\x00\x00\x03sBIT\x08\
\x08\x08\xdb\xe1O\xe0\x00\x00\x01\xe9IDAT(\x91m\x92\xbdk\x13a\x18\xc0\x9f\
\xbb\\r\xd7Ks\xb9&\xc6\xd2j\x8f\xc6D\x08\x8a\xa2\xed\xe2G\x87,\x15\xc4\xb5\
\x8bH\x17-]\x02\x85:\x14\x84\xd0\x82J\x07A\x07\xc1\xff\xc1\xc1I\x04\x07\x11\
\x05\x15\x1d\x1cJ\x87\xa2\xd5\x96\x92&49\xe9\x99\xf4\xbc7w\xf7\xbe\xef\xf3:\
\xdcQ:\xf4\x99\x9e\x8f\x1f\xcf\xb7\xf4\xe9\xf1\xc3\xde\xd7\xcfAg/l5\xe08I\
\x9d\xb2\xd4\xe1\x91\xec\xd5)\xe9\xcd\xad\x1b\x93W.\x9bC\x05.\xfc(&h?\xa6h\
\xec\xe9\xb5\xbbk\x9b\xbbJ\xd0\xd93\xc6n\xd2\xfd\x16\xddo\xc7\x00c\x00\x80\
\x9cE\xa6f\x1a\xc6\xe9\x9c\xfasK\x0e[\rP\x12\x9cx\xd2@*=\xbb(\x8d\x8e!g\xc8\
\x99b\x95rs\x0f\xb8\xaa\xf9\xdd\x03\xa6&\xc5_[>\xecI\x9f\xa9\xa9\x95\x89\xec\
\xbd\xbab\x95\x14\xab\x94\x9f_V+\x13\x85\xd9E\x1f\xa9\xc2)\x00(\x00 \x04\x13\
\x10\x90\xf7\xaf\x92\xe3\x15Y\xd3\xf3\xf3\xcb\x00 k:\xfa\xc4y\xfb\xf20\x97\
\x02\x00\xd0%\xc1\xae\xc36\xb6\x83\xe6\xfd\x93+\xcfdM\x07\x00\xf4I\xa3\xbe\
\xe0o\xfd\x00\x00\x9e\x1b\x8dQ\xf6\x8f0/\xa0\xae/\x05\xec\xe8\x9a0\xe4\xcc\
\xf59"w\\\xc1\xb8\x0c\x00"d\x88"u\xf6\xfc\xc8\xea\xf3\xa8.\xfaD\xd6\xf4\xf1\
\'/\xf4s\x17\x00\x00(\x17!\x8d\xc7B\xa4\xd9\xdbw#ng\xa9\xb6\xb3T\x8b\xe8\xfc\
\x9d9\x00\x10,\x00\xc4\xc4LF+_\xbaHl\xdb\xfb\xf2!Y,\xb7\x9e>"\x9b\x1b\xb4\
\xd3\xf6\xd6\xbe\xcb\xb9Bc\xb5.3\xaa\r\x19\x9df[z}}r\xaaz\xad\xff\xc7>\xb0\
\x9b\xcc\x8d\xcf\xc3\x11#%\x91J\x0e\x9a\x99\xf4\xe0\xc0z\xb3\xa7\xe8V\xd1u\
\x1c#sB\xcb\xa4\x01@`\x185\x17\xd5e\x88\t\xce\xdc^\x1fr\xc3\x8aY\x9d\xfe\xf5\
\xf1\x1dY\xff\xe6m\xff>\xf6]\xd2g\xca\xbaU4\xab\xd3\xff\x01\xe3\xf6\xf0\x91\
\xbc\xe0^J\x00\x00\x00\x00IEND\xaeB`\x82\x7fU\x05\xed' )

def GetXBitmap():
    """Returns a bitmap version of the close button
    @return: bitmap of close button

    """
    return BitmapFromImage(GetXImage())

def GetXImage():
    """Returns an image version of the close button
    @return: image of close button

    """
    stream = cStringIO.StringIO(GetXData())
    return ImageFromStream(stream)

#-----------------------------------------------------------------------------#
# Globals
ID_CLOSE_BUTTON = wx.NewId()
ID_SEARCH_CTRL = wx.NewId()
ID_SEARCH_WORD = wx.NewId()
ID_MATCH_CASE = wx.NewId()
ID_FIND_LBL = wx.NewId()
ID_LINE_CTRL = wx.NewId()
ID_GOTO_LBL = wx.NewId()

#-----------------------------------------------------------------------------#

class CommandBar(wx.Panel):
    """Creates a panel that houses various different command
    controls for the editor.

    """
    def __init__(self, parent, id_, size=(-1, 24), style=wx.TAB_TRAVERSAL):
        """Initializes the bar and its default widgets
        @postcondition: commandbar is created

        """
        wx.Panel.__init__(self, parent, id_, size=size, style=style)

        # Attributes
        self._parent = parent
        self._installed = False
        self._psizer = parent.GetSizer()
        self._h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._goto_sizer = wx.BoxSizer()
        self._search_sizer = wx.BoxSizer()

        # Install Controls
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        self._h_sizer.Add((8, 8))
        bstyle = wx.BU_EXACTFIT
        if wx.Platform == '__WXGTK__':
            bstyle = bstyle | wx.NO_BORDER
        self.close_b = wx.BitmapButton(self, ID_CLOSE_BUTTON, GetXBitmap(), \
                                      size=(14, 14), style=bstyle)
        self._h_sizer.Add(self.close_b, 0, wx.ALIGN_CENTER_VERTICAL)
        self._h_sizer.Add((12, 12))
        v_sizer.Add((2, 2))
        self._h_sizer.Add(v_sizer)
        self.SetSizer(self._h_sizer)
        self.SetAutoLayout(True)

        # Bind Events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=ID_CLOSE_BUTTON)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)

    def Hide(self):
        """Hides the control and notifies the parent
        @postcondition: commandbar is hidden

        """
        wx.Panel.Hide(self)
        if self._psizer != None:
            self._psizer.Layout()
        self._parent.SendSizeEvent()
        self._parent.nb.GetCurrentCtrl().SetFocus()
        return True

    def InstallCtrl(self, id_):
        """Installs a control into the bar by ID
        @postcondition: control is installed
        @return: requested control or None

        """
        if id_ == ID_SEARCH_CTRL:
            ctrl = self.InstallSearchCtrl()
        elif id_ == ID_LINE_CTRL:
            ctrl = self.InstallLineCtrl()
        else:
            ctrl = None
        return ctrl

    def InstallLineCtrl(self):
        """Installs the go to line control into the panel.
        @postcondition: GotoLine control is installed in bar.

        """
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((5, 5))
        linectrl = LineCtrl(self, ID_LINE_CTRL, self._parent.nb.GetCurrentCtrl,
                            size=(100, 20))
        v_sizer.Add(linectrl, 0, wx.ALIGN_CENTER_VERTICAL)
        v_sizer.Add((4, 4))
        go_lbl = wx.StaticText(self, ID_GOTO_LBL, _("Goto Line") + ": ")
        if wx.Platform == '__WXMAC__':
            go_lbl.SetFont(wx.SMALL_FONT)
        h_sizer.Add(go_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        h_sizer.Add((5, 5))
        h_sizer.Add(v_sizer)
        h_sizer.Layout()
        self._goto_sizer = h_sizer
        self._h_sizer.Add(h_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self._h_sizer.Layout()
        return linectrl

    def InstallSearchCtrl(self):
        """Installs the search context controls into the panel.
        Other controls should be removed from the panel before calling
        this method.
        @postcondition: search control is installed in bar

        """
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((5, 5))
        ssize = wx.Size(180, 20)
        if wx.Platform == '__WXGTK__':
            ssize.SetHeight(24)
        search = ed_search.EdSearchCtrl(self, ID_SEARCH_CTRL, 
                                         menulen=5, size=ssize)
        v_sizer.Add(search)
        v_sizer.Add((4, 4))
        f_lbl = wx.StaticText(self, ID_FIND_LBL, _("Find") + u": ")
        mc_sizer = wx.BoxSizer(wx.VERTICAL)
        mc_sizer.Add((7, 7))
        match_case = wx.CheckBox(self, ID_MATCH_CASE, _("Match Case"))
        match_case.SetValue(search.IsMatchCase())
        mc_sizer.Add(match_case)
        mc_sizer.Add((4, 4))
        ww_sizer = wx.BoxSizer(wx.VERTICAL)
        ww_sizer.Add((7, 7))
        ww_cb = wx.CheckBox(self, ID_SEARCH_WORD, _("Whole Word"))
        ww_cb.SetValue(search.IsWholeWord())
        ww_sizer.Add(ww_cb)
        ww_sizer.Add((4, 4))
        if wx.Platform == '__WXMAC__':
            f_lbl.SetFont(wx.SMALL_FONT)
            match_case.SetFont(wx.SMALL_FONT)
            ww_cb.SetFont(wx.SMALL_FONT)
        h_sizer.Add(f_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        h_sizer.Add((5, 5))
        h_sizer.Add(v_sizer)
        h_sizer.Add((10, 10))
        h_sizer.Add(mc_sizer)
        h_sizer.Add((10, 10))
        h_sizer.Add(ww_sizer)
        self._search_sizer = h_sizer
        self._h_sizer.Add(h_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self._h_sizer.Layout()
        return search

    def OnCheck(self, evt):
        """Check box event handler
        @param evt: Event that called this handler
        @type evt: wx.EVT_CHECKBOX

        """
        e_id = evt.GetId()
        if e_id in [ID_MATCH_CASE, ID_SEARCH_WORD]:
            flag_map = { ID_MATCH_CASE : wx.FR_MATCHCASE,
                         ID_SEARCH_WORD : wx.FR_WHOLEWORD
                        }
            ctrl = self.FindWindowById(e_id)
            if ctrl != None:
                val = ctrl.GetValue()
                search = self.FindWindowById(ID_SEARCH_CTRL)
                if search != None:
                    if val:
                        search.SetSearchFlag(flag_map[e_id])
                    else:
                        search.ClearSearchFlag(flag_map[e_id])
        else:
            evt.Skip()

    def OnClose(self, evt):
        """Closes the panel and cleans up the controls
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        if e_id == ID_CLOSE_BUTTON:
            self.Hide()
            #self.Uninstall()
        else:
            evt.Skip()

    def OnPaint(self, evt):
        """Paints the background of the bar with a nice gradient.
        @param evt: Event that called this handler
        @type evt: wx.PaintEvent

        """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        col2 = util.AdjustColour(col1, 50)
        col1 = util.AdjustColour(col1, -50)
        grad = gc.CreateLinearGradientBrush(0, 1, 0, 29, col2, col1)
        rect = self.GetRect()

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width - 0.5, rect.height - 0.5)

        gc.SetPen(wx.Pen(util.AdjustColour(col1, -60), 1))
        gc.SetBrush(grad)
        gc.DrawPath(path)

        evt.Skip()

    def Show(self, id_=0):
        """Shows the control and installs it in the parents
        sizer if not installed already.
        @param id_: Id of control to show in bar

        """
        # Install self in parent
        if not self._installed and self._psizer != None:
            self._installed = True
            self._psizer.Add(self, 0, wx.EXPAND)
            self._psizer.Layout()
            self._parent.SendSizeEvent()
        wx.Panel.Show(self)

        # HACK YUCK, come back and try again when my brain is working
        # Show specified control
        if id_:
            ctrl = self.FindWindowById(id_)
            if ctrl is None:
                ctrl = self.InstallCtrl(id_)

            # First Hide everything
            for kid in self._search_sizer.GetChildren():
                kid.Show(False)

            for kid in self._goto_sizer.GetChildren():
                kid.Show(False)

            if id_ == ID_SEARCH_CTRL:
                for kid in self._search_sizer.GetChildren():
                    kid.Show(True)
                self._search_sizer.Layout()
            elif id_ == ID_LINE_CTRL:
                for kid in self._goto_sizer.GetChildren():
                    kid.Show(True)

            self.GetSizer().Layout()
            if ctrl != None:
                ctrl.SetFocus()
                ctrl.SelectAll()

    def Uninstall(self):
        """Uninstalls self from parent control
        @postcondition: removes self from parent sizer

        """
        for item in self.GetChildren():
            item.Destroy()
        self._psizer.Remove(self)
        self._psizer.Layout()
        self._parent.SendSizeEvent()
        self.Destroy()

    def UninstallCtrl(self, id_):
        """Hides the sizer object holding the control with the passed in id
        @param obId: id of control to remove
        @postcondition: control is removed from bar

        """
        ctrl = self.FindWindowById(id_)
        if ctrl != None:
            c_sizer = ctrl.GetContainingSizer()
            sizer = self.GetSizer()
            sizer.Hide(c_sizer, True)
            sizer.Layout()

# TODO will finish implementation once the key events are working in the
#      search control for windows.
class CommandExecuter(wx.SearchCtrl):
    """Puts the editor into command mode to catch and execute
    key commands.
    @status: not implemented waiting for some fixes in wx
    
    """
    def __init__(self, parent, id_, pos=wx.DefaultPosition, \
                size=wx.DefaultSize):
        """Initializes the CommandExecuter"""
        wx.SearchCtrl.__init__(self, parent, id_, "", pos, size, 
                               wx.TE_PROCESS_ENTER)
                               
        # Hide the search button and text
        self.ShowSearchButton(False)
        self.SetDescriptiveText(wx.EmptyString)

        # Event management
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)

    def ExecuteCommand(self, cmd_str):
        """Interprets and executes a command
        @status: not implemented

        """
        

    def OnEnter(self, evt):
        """Get the currently entered command string and
        execute it.
        @status: not implemented
        
        """
        

    def OnKeyUp(self, evt):
        """Records the key sequence that has been entered and
        then executes the command if a valid sequence is entered.
        @status: not implemented

        """
        
# wxBug Validator doesnt work on Windows due to the SearchCtrl on
#       that platform not emitting EVT_CHAR.
class LineCtrl(wx.SearchCtrl):
    """A custom int control for providing a go To line control
    for the Command Bar. The get_doc parameter needs to be of
    type callable and needs to return the document object that
    the action is to take place in.

    """
    def __init__(self, parent, id_, get_doc, size=wx.DefaultSize):
        """Initializes the LineCtrl control and its attributes.
        @postcondition: gotoline control is initialized

        """
        wx.SearchCtrl.__init__(self, parent, id_, "", size=size,
                             style=wx.TE_PROCESS_ENTER,
                             validator=util.IntValidator(0, 65535))

        # Attributes
        self._last = 0
        self.GetDoc = get_doc

        # Hide the search button and text
        self.ShowSearchButton(False)
        self.ShowCancelButton(False)
        self.SetDescriptiveText(wx.EmptyString)

        # MSW/GTK HACK
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    child.SetValidator(util.IntValidator(0, 65535))

        # Event management
        self.Bind(wx.EVT_TEXT_ENTER, self.OnInput)

    def OnInput(self, evt):
        """Processes the entered line number
        @param evt: Event that called this handler
        @type evt: wx.EVT_TEXT_ENTER

        """
        val = self.GetValue()
        if not val.isdigit():
            return
        val = int(val) - 1
        doc = self.GetDoc()
        lines = doc.GetLineCount()
        if val > lines:
            val = lines
        doc.GotoLine(val)
        doc.SetFocus()
        evt.Skip()
