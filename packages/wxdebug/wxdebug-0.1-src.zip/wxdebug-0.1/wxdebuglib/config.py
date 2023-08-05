import wx
from os.path import realpath, dirname, join, isdir, exists
from os import popen, getcwd
import meta
from patterns.singleton import Singleton

wxdebug_path = None

def wxDebugPath():
    global wxdebug_path
    
    if not wxdebug_path:
        #wxdebug_path = realpath( join( dirname(realpath(__file__)) ,'..') )
        wxdebug_path = getcwd()
    
    return wxdebug_path

class Config(wx.FileConfig):
    
    __metaclass__ = Singleton
    
    def __init__(self, wxdebug_path = wxDebugPath()):
        wx.FileConfig.__init__(self, localFilename = join(wxdebug_path, 'wxdebug.ini'))
        self.SetRecordDefaults(True)
        self.wxdebug_path = wxdebug_path
        self.inifile = join(wxdebug_path, 'wxdebug.ini')
        
        if not exists(self.inifile):
            file = open(self.inifile, "w")
            file.close()
    
    def ReadXdebugPath(self):
        return self.Read('xdebug_path',self.defaultXdebugPath())
    
    def defaultXdebugPath(self):
        xdebug_path = popen('php -r "if ( !extension_loaded(\'xdebug\') ) { exit(1); }'\
                                + '$xdebug_path = ini_get(\'xdebug.profiler_output_dir\');'\
                                + 'if ( empty($xdebug_path) || !is_dir($xdebug_path) ) { exit(1); }'\
                                + 'print $xdebug_path; exit(0);"').read()
        if isdir(xdebug_path):
            return xdebug_path
        return self.wxdebug_path
    
    def WriteXdebugPath(self, value):
        self.Write('xdebug_path',value)
        self.Flush()
    
    def ReadExplorerRefresh(self):
        explorer_refresh = self.ReadInt('explorer_refresh',self.defaultExplorerRefresh())
        if not explorer_refresh:
            explorer_refresh = self.defaultExplorerRefresh()
        return explorer_refresh
    
    def defaultExplorerRefresh(self):
        return 5000
    
    def WriteExplorerRefresh(self, value):
        self.WriteInt('explorer_refresh', value)
        self.Flush()


