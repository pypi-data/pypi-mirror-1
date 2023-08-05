import wx
import meta, analyzer, loader
from config import Config
from profile import Profile
import gui.explorer as explorer, gui.calltree as calltree, gui.detail as detail, gui.settings as settings
import os.path

class MainFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, meta.name, size=(800,600))
        
        self.SetIcon(wx.ArtProvider_GetIcon(wx.ART_LIST_VIEW, wx.ART_FRAME_ICON, (16,16)))
        
        statusbar = self.CreateStatusBar()
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.createMenuBar()
        self.createToolbar(self.initialToolbar())
        
        self.pmanager = ProfilePanelManager(self)
        
        loader.EVT_START(self,self.OnLoadStart)
        loader.EVT_STOP(self,self.OnLoadStop)
        loader.EVT_PROGRESS(self,self.OnLoadProgress)
        loader.EVT_FAIL(self,self.OnLoadFail)
        
    def menus(self):
        return (("&File",
                    ("&Open...", "Open Xdebug file", self.OnOpen),
                    ("&Close", "Close Xdebug file", self.OnClose),
                    (None,None,None),
                    ("E&xit", "Exit", self.OnCloseWindow)),
                ("&Tools",
                    ("&Explorer", "Profile explorer", self.OnExplorer),
                    ("&Settings", "wxDebug Settings", self.OnSettings)),
                ("&Help",
                    ("&About", "Program information", self.OnAbout)),
            )
                    
    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for menu in self.menus():
            label = menu[0]
            items = menu[1:]
            menuBar.Append(self.createMenu(items), label)
        self.SetMenuBar(menuBar)
    
    def createMenu(self, menuItems):
        menu = wx.Menu()
        for label, status, handler in menuItems:
            if not label:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1, label, status)
            self.Bind(wx.EVT_MENU, handler, menuItem)
        return menu
    
    def initialToolbar(self):
        return (
                (None,None,None),
                (wx.ART_FILE_OPEN,"Open Xdebug file",self.OnOpen),
                (None,None,None),
                (wx.ART_FIND,"Profile Explorer",self.OnExplorer),
            )
    
    def profileToolbar(self):
        return (
                (None,None,None),
                (wx.ART_FILE_OPEN,"Open Xdebug file",self.OnOpen),
                (wx.ART_CROSS_MARK,"Close Xdebug file",self.OnClose),
                (None,None,None),
                (wx.ART_REDO,"Reload Profile",self.OnReload),
                (None,None,None),
                (wx.ART_FIND,"Profile Explorer",self.OnExplorer),
            )
    
    def createToolbar(self, tbdata):
        
        if self.__dict__.has_key('tb'):
            self.tb.Destroy()
            del self.tb
        
        self.tb = self.CreateToolBar( wx.TB_HORIZONTAL
                                 | wx.NO_BORDER
                                 | wx.TB_FLAT
                                 | wx.TB_TEXT
                                 )
        
        for tbitem in tbdata:
            if tbitem[0] is None:
                self.tb.AddSeparator()
            else:
                bmp = wx.ArtProvider.GetBitmap(tbitem[0], wx.ART_TOOLBAR)
                tid = wx.NewId()
                self.tb.AddSimpleTool(tid, bmp, tbitem[1])
                self.Bind(wx.EVT_TOOL, tbitem[2], id=tid)
        
        self.tb.Realize()
    
    
    wildcard = "Xdebug files (cachegrind.out.*)|cachegrind.out.*|All files (*.*)|*.*"
    
    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Open Xdebug file...",Config().ReadXdebugPath(), style=wx.OPEN | wx.HIDE_READONLY, wildcard = self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            self.loadFile(path)
        else:
            dlg.Destroy()
            
    def OnReload(self, event):
        self.loadFile(Profile().name)
        
    def loadFile(self, path):
        try:
            Profile.deleteInstance()
            Profile(path)
        except IOError, e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)
            return
        self.loader = loader.Loader(self)
    
    def OnLoadStart(self, event):
        self.progressmeter = wx.ProgressDialog("Loading Xdebug file",'% Loaded',\
            100, style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
    
    def OnLoadStop(self, event):
        self.progressmeter.Destroy()
        self.SetTitle(meta.name + ' -- ' + Profile().script)
        del self.loader
        self.createToolbar(self.profileToolbar())
        self.pmanager.open()
    
    def OnLoadProgress(self, event):
        if not self.progressmeter.Update(event.percentloaded):
            self.loader.abort()
            del self.loader
            self.progressmeter.Destroy()
    
    def OnLoadFail(self, event):
        self.progressmeter.Destroy()
        wx.MessageBox("Unable to open "+Profile().name+": "+str(event.e), 'Bad File', wx.OK | wx.ICON_ERROR)
    
    def destroyProgressMeter(self):
        if self.__dict__.has_key('progressmeter'):
            self.progressmeter.Destroy()
    
    def OnClose(self, event):
        self.SetTitle(meta.name)
        self.pmanager.close()
        self.createToolbar(self.initialToolbar())
    
    def OnExplorer(self, event):
        if not self.__dict__.has_key('explorer'):
            self.explorer = explorer.Explorer(self)
        
        try:
            if not self.explorer.IsShown():
                self.explorer.Show()
            else:
                self.explorer.Hide()
        except:
            del self.explorer
            self.OnExplorer(event)
    
    def OnSettings(self, event):
        dlg = settings.SettingsDialog()
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnAbout(self, event):
        pass
    
    def OnCloseWindow(self, event):
        self.Destroy()

class ProfilePanelManager:
    
    def __init__(self, parent):
        self.parent = parent

    def open(self):
        
        if self.__dict__.has_key('panel'):
            self.panel.Destroy()
            del self.panel
        
        self.panel = ProfilePanel(self.parent)
    
    def close(self):
        if self.__dict__.has_key('panel'):
            self.panel.Destroy()
            del self.panel

class ProfilePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour("White")
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add((5,0))
        
        self.tree = calltree.Calltree(self)
        sizer.Add(self.wrapInStaticBox('Calltree',self.tree,(260,500)), 1, wx.EXPAND|wx.ALL, 5)
        
        sizer.Add((5,0))
        
        self.detail = detail.Detail(self)
        sizer.Add(self.wrapInStaticBox('Detail',self.detail,(530,500)), 2, wx.EXPAND|wx.ALL, 5)
        
        sizer.Add((5,0))
        
        self.SetSizer(sizer)
        
        self.tree.detail = self.detail
        
        self.tree.open()
        
        #self.detail.display(dumpfile.script, {}, [])
        
        sizer.Fit(parent)
        
        self.SetBestFittingSize()
        
    
    def wrapInStaticBox(self, label, child, minsize):
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.SetMinSize(minsize)
        sizer.Add(child, 1, wx.EXPAND|wx.ALL)
        sizer.Layout()
        return sizer
