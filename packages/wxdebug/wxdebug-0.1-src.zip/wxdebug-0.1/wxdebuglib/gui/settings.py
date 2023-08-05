import wx

from config import Config

class SettingsDialog(wx.Dialog):
    
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "wxDebug Settings")
        
        about   = wx.StaticText(self, -1, "Change your wxDebug settings...")
        xdebug_path_l  = wx.StaticText(self, -1, "Xdebug Path:")
        explorer_refresh_l = wx.StaticText(self, -1, "Explorer Refresh (ms):")
        
        self.xdebug_path_t  = wx.TextCtrl(self,size=(160, -1))
        self.xdebug_path_t.SetValue(Config().ReadXdebugPath())
        
        self.explorer_refresh_t = wx.TextCtrl(self)
        self.explorer_refresh_t.SetValue(str(Config().ReadExplorerRefresh()))

        # Use standard button IDs
        okay   = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)
        
        browse = wx.Button(self, -1, "Browse")

        # Layout with sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(about, 0, wx.ALL, 5)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
        
        fgs1 = wx.FlexGridSizer(1, 3, 5, 5)
        fgs1.Add(xdebug_path_l, 0, wx.ALIGN_RIGHT)
        fgs1.Add(self.xdebug_path_t, 0, wx.EXPAND)
        fgs1.Add(browse, 0, wx.ALIGN_RIGHT)
        
        sizer.Add(fgs1, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
        
        fgs2 = wx.FlexGridSizer(1, 2, 5, 5)
        fgs2.Add(explorer_refresh_l, 0, wx.ALIGN_RIGHT)
        fgs2.Add(self.explorer_refresh_t, 0, wx.EXPAND)
        
        sizer.Add(fgs2, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

        btns = wx.StdDialogButtonSizer()
        btns.AddButton(okay)
        btns.AddButton(cancel)
        btns.Realize()
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
        
        self.Bind(wx.EVT_BUTTON, self.OnOkay, okay)
        self.Bind(wx.EVT_BUTTON, self.OnBrowse, browse)
        
        
        self.CenterOnScreen()
    
    def OnOkay(self, event):
        if Config().ReadXdebugPath() != self.xdebug_path_t.GetValue():
            Config().WriteXdebugPath(self.xdebug_path_t.GetValue())
        
        if Config().ReadExplorerRefresh() != int(self.explorer_refresh_t.GetValue()):
            Config().WriteExplorerRefresh(int(self.explorer_refresh_t.GetValue()))
        
        event.Skip()

    
    def OnBrowse(self, event):
        dialog = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE ^ wx.DD_NEW_DIR_BUTTON, defaultPath = self.xdebug_path_t.GetValue())
        if dialog.ShowModal() == wx.ID_OK:
            self.xdebug_path_t.SetValue(dialog.GetPath())
        dialog.Destroy()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    
    dlg = SettingsDialog()
    dlg.ShowModal()
    dlg.Destroy()
    
    app.MainLoop()
