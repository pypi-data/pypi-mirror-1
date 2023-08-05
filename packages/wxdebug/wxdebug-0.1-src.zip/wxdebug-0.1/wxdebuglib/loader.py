import wx
from threading import *
from profile import Profile

EVT_START_ID = wx.NewId()
EVT_PROGRESS_ID = wx.NewId()
EVT_STOP_ID = wx.NewId()
EVT_FAIL_ID = wx.NewId()

class StartEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_START_ID)
        
class ProgressEvent(wx.PyEvent):
    def __init__(self, percentloaded):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PROGRESS_ID)
        self.percentloaded = percentloaded

class StopEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_STOP_ID)

class FailEvent(wx.PyEvent):
    def __init__(self, e):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_FAIL_ID)
        self.e = e

def EVT_START(win, func):
    win.Connect(-1, -1, EVT_START_ID, func)

def EVT_PROGRESS(win, func):
    win.Connect(-1, -1, EVT_PROGRESS_ID, func)

def EVT_STOP(win, func):
    win.Connect(-1, -1, EVT_STOP_ID, func)

def EVT_FAIL(win, func):
    win.Connect(-1, -1, EVT_FAIL_ID, func)

class Loader(Thread):
    
    def __init__(self, frame):
        Thread.__init__(self)
        self.frame = frame
        self._want_abort = 0
        self.start()
    
    def run(self):
        
        wx.PostEvent(self.frame, StartEvent())
        
        try:
            Profile().load(self.progressCallback)
        except Exception, e:
            wx.PostEvent(self.frame, FailEvent(e))
            return
        
        if self._want_abort:
            return
        
        wx.PostEvent(self.frame, StopEvent())
        
    def abort(self):
        self._want_abort = 1
    
    def progressCallback(self, percentloaded):
        wx.PostEvent(self.frame, ProgressEvent(percentloaded))
        
        if self._want_abort:
            return False
        
        return True
