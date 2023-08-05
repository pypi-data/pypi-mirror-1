import wx
import os.path
from profile import Profile

class Calltree(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1, style=wx.NO_BORDER|wx.TR_DEFAULT_STYLE)
    
    def open(self):
        p = Profile()
        self.total = p.summary
        self.stats = p.functionstats
        self.DeleteAllItems()
        
        # Setup the root node
        root = self.AddRoot(os.path.basename(p.script))
        payload = {'self': p.stack[0], 'children': p.stack[1], 'called': {}}
        self.SetItemPyData(root, payload)
        self.SetItemHasChildren(root, True)
        self.Expand(root)
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnItemExpanding, self)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self)
        
    def close(self):
        self.DeleteAllItems()
    
    def AddTreeNodes(self, parentItem):
        payload = self.GetItemPyData(parentItem)
        i = 0
        
        if not type(payload['children']) == list: return
        
        for item in payload['children']:
            if type(item) == dict:
                newItem = self.AppendItem(parentItem, item['name'])
                newPayload = {'self': item, 'children': [], 'called': payload['self']['stack'][i]}
                self.SetItemPyData(newItem, newPayload)
            else:
                newItem = self.AppendItem(parentItem, item[0]['name'])
                newPayload = {'self': item[0], 'children': item[1], 'called': payload['self']['stack'][i]}
                # May need a lazy list - looks like SetItemPyData has issues with big datasets
                if len(item[1]) > 0:
                    self.SetItemPyData(newItem, newPayload)
                    self.SetItemHasChildren(newItem, True)
            i += 1
    
    def OnItemExpanding(self, evt):
        self.AddTreeNodes(evt.GetItem())
        
    def OnItemCollapsed(self, evt):
        parentItem = evt.GetItem()
        self.DeleteChildren(parentItem)

    def OnSelChanged(self, evt):
        item = evt.GetItem()
        payload = self.GetItemPyData(item)
        self.detail.display(payload['self'], payload['called'], self.total, self.stats)
        
