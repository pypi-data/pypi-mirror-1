import wx
import wx.lib.mixins.listctrl as listmix
from profiles import Profiles

from config import Config
import math

class Explorer(wx.MiniFrame):
    """
    Provides view of list of files in the Xdebug output directory, which is "refreshed"
    at intervals so that newest files appear at the top of the list
    """
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, " wxDebug Explorer: "+Config().ReadXdebugPath(),\
            wx.DefaultPosition, (600,200), wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        
        self.list = ExplorerList(self)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.list.OnTimer, self.timer)
        
        self.CenterOnScreen()
    
    def Show(self):
        if not self.timer.IsRunning():
            self.timer.Start(Config().ReadExplorerRefresh())
        wx.MiniFrame.Show(self)
    
    def Hide(self):
        if self.timer.IsRunning():
            self.timer.Stop()
        wx.MiniFrame.Hide(self)
    
class ExplorerList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, \
            style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES )
        
        self.il = wx.ImageList(16, 16)
        a={"sm_up":"GO_UP","sm_dn":"GO_DOWN","s_idx":"NORMAL_FILE"}
        for k,v in a.items():
            # TODO - purge the eval!
            s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
            exec(s)
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        
        self.profiles = Profiles()
        
        self.prepareRowColours()
        self.addColumns()
        self.addRows()
        
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 3)
        
        self.SortListItems(1,0)
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
    
    def prepareRowColours(self):
        self.rowcolour1 = wx.ListItemAttr()
        self.rowcolour1.SetBackgroundColour("white")
        self.rowcolour2 = wx.ListItemAttr()
        self.rowcolour2.SetBackgroundColour("light grey")
    
    def columnData(self):
        return (
                (1,"Script", wx.LIST_FORMAT_LEFT ),
                (2,"Last Modified", wx.LIST_FORMAT_RIGHT ),
                (3,"Size (kb)",wx.LIST_FORMAT_RIGHT ),
               )
    
    def addColumns(self):
        for col, heading, format in self.columnData():
            self.InsertColumn(col, heading, format)
        
        self.SetColumnWidth(0, 300)
        self.SetColumnWidth(1, 150)
        self.SetColumnWidth(2, 100)
    
    def addRows(self):
        self.DeleteAllItems()
        files = {}
        key = 0
        self.scriptMap = {}
        
        # TODO: Decorate iterator
        for file in self.profiles.files:
            try:
                stringDate = self.toStringDate(file.mtime)
                kb = self.toKb(file.size)
                files[key] = (file.script, stringDate, kb, file.name)
                self.scriptMap[file.script] = file.name
                key += 1
            except:
                pass
        self.itemDataMap = files
        self.itemIndexMap = files.keys()
        self.SetItemCount(len(files))
        
    def toStringDate(self, mtime):
        return wx.DateTimeFromTimeT(mtime).Format('%Y-%m-%d %H:%M:%S')
    
    def toKb(self, size):
        kb = size / (1024.0)
        return "%.1f"%kb
    
    def OnTimer(self, event):
        if not self.profiles.hasChanged():
            return
        self.profiles = Profiles()
        self.addRows()
        self.SortListItems(1,0)
    
    def OnColClick(self,event):
        event.Skip()
    
    def OnActivated(self, event):
        try:
            script = event.GetItem().GetText()
            miniframe = self.GetParent()
            frame = miniframe.GetParent().loadFile(self.scriptMap[script])
            miniframe.Hide()
        except:
            pass
    
    def OnGetItemText(self, item, col):
        index=self.itemIndexMap[item]
        s = self.itemDataMap[index][col]
        return s
    
    def OnGetItemImage(self, item):
        return self.s_idx
    
    def OnGetItemAttr(self, item):
        if math.floor(item % 2.0) == 0:
            return self.rowcolour1
        return self.rowcolour2
    
    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items
        self.Refresh()
    
    def GetColumnSorter(self):
        if self._col == 2:
            return self.StrToFloatSorter
        return listmix.ColumnSorterMixin.GetColumnSorter(self)
    
    def StrToFloatSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]
        
        try:
            
            if not ascending:
                item1, item2 = item2, item1 
            
            item1 = float(item1) * 10
            item2 = float(item2) * 10
            return int(round(item1-item2))
        except:
            return 0
    
    def GetListCtrl(self):
        return self
        
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

