import sys

import wxdebuglib
libpath = wxdebuglib.__path__[0]
sys.path.insert(0, libpath) 
del wxdebuglib

import wx

class wxApp(wx.App):
    def OnInit(self):
        return True


class App(object):
    def __init__(self):
        self.wxApp = wxApp(0)
        self.init()
        self.mainframe.Show()
        self.wxApp.MainLoop()

    def init(self):
        import wxdebuglib.gui.mainframe
        self.mainframe = wxdebuglib.gui.mainframe.MainFrame()
    
    def quit(self):
        self.wxApp.ProcessIdle()
        self.wxApp.Exit()

def start():
    App()

if __name__ == '__main__':
    start()
