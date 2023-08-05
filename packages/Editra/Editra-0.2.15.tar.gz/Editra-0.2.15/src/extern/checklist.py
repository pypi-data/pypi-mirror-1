import wx
import listctrl
#import wx.lib.mixins.listctrl as listctrl

class TestFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title)
        
        list = TestList(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(list, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize()
        self.Show()

class TestList(wx.ListCtrl, listctrl.CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition, (500, 500), 
                             style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES)

        self.InsertColumn(0, "Column 1")
        self.InsertColumn(1, "Column 2")
        self.InsertColumn(2, "Column 3")
        self.InsertColumn(3, "Column 4")

        listctrl.CheckListCtrlMixin.__init__(self)

        for x in xrange(10):
            self.InsertStringItem(x, "This is column %d in row %d" % (1, x))
            self.SetStringItem(x, 1, "This is column %d in row %d" % (2, x))
            self.SetStringItem(x, 2, "This is column %d in row %d" % (3, x))
            self.SetStringItem(x, 3, "This is column %d in row %d" % (4, x))

if __name__ == '__main__':
    app = wx.PySimpleApp(False)
    frame = TestFrame(None, "LIST TEST")
    app.MainLoop()
