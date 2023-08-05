import wx
import wx.lib.mixins.listctrl as listmix
import math
from os.path import basename
import re

class Detail(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.spanel = wx.Panel(self)
        
        self.itemname = wx.StaticText(self.spanel, -1, '',(10,10))
        self.script = wx.StaticText(self.spanel, -1, '',(10,30))
        self.time = wx.StaticText(self.spanel, -1, '',(10,50))
        
        sizer.Add(self.spanel, 1, wx.EXPAND|wx.ALL)
        
        self.nb = wx.Notebook(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP)
        self.nb.SetBackgroundColour('White')
        
        self.lblpanel = LineByLinePanel(self.nb)
        self.nb.AddPage(self.lblpanel, 'Line by Line')
        
        self.opanel = OverallPanel(self.nb)
        self.nb.AddPage(self.opanel, 'Overall')
        
        sizer.Add(self.nb, 5, wx.EXPAND|wx.ALL)
        
        self.SetSizer(sizer)
        sizer.Fit(self.nb)
    
    def display(self, item, called, total, stats):
        
        self.itemname.Destroy()
        self.script.Destroy()
        self.time.Destroy()
        
        self.itemname = wx.StaticText(self.spanel, -1, item['name'],(10,10))
        self.script = wx.StaticText(self.spanel, -1, "File: "+item['script'],(10,30))
        
        try:
            sms = float(item['time']) / 10000.0
            spc = (float(item['time']) / float(total)) * 100.0
            sts = "Self Time: %01.3fms (%01.2f%%)" % (sms, spc)
        except:
            sts = "Self Time: - "
        
        if len(item['stack']) > 0:
            try:
                cms = float(called['time']) / 10000.0
                cpc = (float(called['time']) / float(total)) * 100.0
                cts = ", Cumulative Time: %01.3fms (%01.2f%%)" % (cms, cpc)
            except:
                cts = ""
        else:
            cts = ""
        
        self.time = wx.StaticText(self.spanel, -1, sts+cts,(10,50))
        
        if not item.has_key('stack'):
            item['stack'] = []
            
        # Data massaging loop: really needs to be some kind of Decorator
        lbl = []
        overall = []
        for fn in item['stack']:
            try:
                lblfn = {}
                lblfn['name'] = fn['name']
                
                # Need to locate child to get this... (skip for now)
                #lblfn['selft'] = None
                
                lblfn['cumt'] = fn['time']
                lblfn['script'] = stats[fn['name']]['script']
                lblfn['cscript'] = item['script']
                lblfn['cscriptline'] = fn['lineno']
                lbl.append(lblfn)
                
                ofn = stats[fn['name']]
                ofn['name'] = fn['name']
                overall.append(ofn)
            except Exception, e:
                # Fails on root node (TODO)
                pass
        
        self.lblpanel.list.addRows(lbl)
        self.opanel.list.addRows(overall)

class ListPanel(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
    
    def addList(self, list):
        self.sizer.Add(list, 1, wx.EXPAND|wx.ALL)
    
class LineByLinePanel(ListPanel):
    def __init__(self, parent):
        ListPanel.__init__(self, parent)
        self.list = LineByLineList(self)
        self.addList(self.list)

class OverallPanel(ListPanel):
    def __init__(self, parent):
        ListPanel.__init__(self, parent)
        self.list = OverallList(self)
        self.addList(self.list)

class FunctionList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, numcols):
        wx.ListCtrl.__init__(self, parent, -1, \
            style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES )
        
        self.il = wx.ImageList(16, 16)
        a={"sm_up":"GO_UP","sm_dn":"GO_DOWN","s_idx":"NORMAL_FILE"}
        for k,v in a.items():
            # TODO - purge the eval!
            s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
            exec(s)
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        
        self.prepareRowColours()
        self.addColumns()
        
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, numcols)
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        
    def prepareRowColours(self):
        self.rowcolour1 = wx.ListItemAttr()
        self.rowcolour1.SetBackgroundColour("white")
        self.rowcolour2 = wx.ListItemAttr()
        self.rowcolour2.SetBackgroundColour("light grey")
    
    def columnData(self):
        pass
    
    def addColumns(self):
        i = 0
        for col, heading, format, width in self.columnData():
            self.InsertColumn(col, heading, format)
            self.SetColumnWidth(i, width)
            i += 1
    
    def addRows(self, functions):
        pass
        
    def OnColClick(self,event):
        event.Skip()
    
    def OnActivated(self, event):
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

    def GetListCtrl(self):
        return self
        
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)
    
    def MsSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]
        
        item1 = item1[0:len(item1)-2]
        item2 = item2[0:len(item2)-2]
        
        try:
            
            if not ascending:
                item1, item2 = item2, item1 
            
            item1 = float(item1) * 1000
            item2 = float(item2) * 1000
            return int(round(item1-item2))
        except:
            return 0

class LineByLineList(FunctionList):
    
    calledfromp = re.compile('^\s*(.*) \(([0-9]+)\)\s*$')
    
    def __init__(self, parent):
        FunctionList.__init__(self, parent, 5)
    
    def columnData(self):
        return (
            (1, "", wx.LIST_FORMAT_RIGHT, 20),
            (2, "Function", wx.LIST_FORMAT_LEFT, 150),
            #(3, "Self", wx.LIST_FORMAT_RIGHT, 75),
            (3, "Cum.", wx.LIST_FORMAT_RIGHT, 75),
            (4, "File", wx.LIST_FORMAT_LEFT, 125),
            (5, "Called From", wx.LIST_FORMAT_LEFT, 130),
        )
    
    def addRows(self, functions):
        self.DeleteAllItems()
        
        # TODO: more need for Decorators
        fnlist = {}
        key = 0
        for fn in functions:
            try:
                #st = float(fn['selft']) / 10000
                #st = "%01.3fms" % st
                ct = float(fn['cumt']) / 10000
                ct = "%01.3fms" % ct
                
                s = basename(fn['script'])
                cs = basename(fn['cscript']) + ' ('+fn['cscriptline']+')'
                #fnlist[key] = (str(key), fn['name'], st, ct, s, cs)
                fnlist[key] = (str(key), fn['name'], ct, s, cs)
                key += 1
            except Exception, e:
                pass
        
        self.itemDataMap = fnlist
        self.itemIndexMap = fnlist.keys()
        self.SetItemCount(len(fnlist))
        self.Refresh()
    
    def CalledFromSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]
        
        if not ascending:
            item1, item2 = item2, item1
        
        item1m = self.calledfromp.match(item1)
        if not item1m:
            return 0
        
        item2m = self.calledfromp.match(item2)
        if not item1m:
            return 0
        
        cmpVal = cmp(item1m.group(1), item2m.group(1))
        
        if cmpVal != 0:
            return cmpVal
        
        try:
            return cmp(int(item1m.group(2)), int(item2m.group(2)))
        except:
            return 0
    
    def GetColumnSorter(self):
        if self._col == 2:
            return self.MsSorter
        if self._col == 4:
            return self.CalledFromSorter
        return listmix.ColumnSorterMixin.GetColumnSorter(self)

class OverallList(FunctionList):
    
    def __init__(self, parent):
        FunctionList.__init__(self, parent, 7)
    
    def columnData(self):
        return (
            (1, "", wx.LIST_FORMAT_RIGHT, 20),
            (2, "Function", wx.LIST_FORMAT_LEFT, 150),
            (3, "Avg Self", wx.LIST_FORMAT_RIGHT, 75),
            (4, "Avg Cum.", wx.LIST_FORMAT_RIGHT, 75),
            (5, "Total Self", wx.LIST_FORMAT_RIGHT, 75),
            (6, "Total Cum.", wx.LIST_FORMAT_RIGHT, 75),
            (7, "Calls", wx.LIST_FORMAT_RIGHT, 30),
        )
    
    def addRows(self, functions):
        self.DeleteAllItems()
        
        # TODO: more need for Decorators
        fnlist = {}
        key = 0
        for fn in functions:
            try:
                #{'selft': 6022, 'cumt': 34366, 'calls': 11},
                as = (float(fn['selft']) / fn['calls']) / 10000
                as = "%01.3fms" % as
                
                ac = (float(fn['cumt']) / fn['calls']) / 10000
                ac = "%01.3fms" % ac
                
                ts = float(fn['selft']) / 10000
                ts = "%01.3fms" % ts
                
                tc = float(fn['cumt']) / 10000
                tc = "%01.3fms" % tc
                
                fnlist[key] = (str(key),fn['name'], as, ac, ts, tc, str(fn['calls']))
                key += 1
            except Exception, e:
                pass
        
        self.itemDataMap = fnlist
        self.itemIndexMap = fnlist.keys()
        self.SetItemCount(len(fnlist))
    
    def CallsSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]
        
        if not ascending:
            item1, item2 = item2, item1
        
        try:
            item1 = int(item1)
            item2 = int(item2)
            return item1-item2
        except:
            return 0
    
    def GetColumnSorter(self):
        if self._col >= 2 and self._col <= 5:
            return self.MsSorter
        if self._col == 6:
            return self.CallsSorter
        return listmix.ColumnSorterMixin.GetColumnSorter(self)

