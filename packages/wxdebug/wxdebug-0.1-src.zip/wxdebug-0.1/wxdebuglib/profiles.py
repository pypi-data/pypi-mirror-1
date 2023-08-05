import os, re
from os.path import isfile, join
from stat import *

from config import Config
from profile import ExistingProfile

class Profiles:
    """
    Provides access to a list of the profiles in a single directory
    as well as being able to monitor whether any of those files changed
    """
    
    p = re.compile('^cachegrind\.out\.[0-9]+$')
    
    def __init__(self, directory = None):
        self.mtime = 0
        self.files = []
        self._filemap = {}
        if directory is None:
            directory = Config().ReadXdebugPath()
        self.directory = directory
        self._initialize(directory)
    
    def _initialize(self, directory):
        for file in os.listdir(directory):
            if isfile(join(directory,file)) and self.p.match(file):
                df = ExistingProfile(join(directory,file))
                self.files.append(df)
                self._filemap[file] = df
                if df.mtime > self.mtime:
                    self.mtime = df.mtime
    
    def hasChanged(self):
        change = False
        # Should benchmark / explorer faster techniques...
        for file in os.listdir(self.directory):
            fullfile = join(self.directory,file)
            if isfile(fullfile) and self.p.match(file):
                if os.stat(fullfile)[ST_MTIME] > self.mtime:
                    change = True
        return change
    
    def __iter__(self):
        return self.files.__iter__()

if __name__ == '__main__':
    ps = Profiles()
    
    for p in ps:
        print p.name
        try:
            print p.script
        except:
            print "Bad file"
    
    """
    if d.hasChanged():
        print "Changed"
    else:
        print "No change"
    
    f = open(os.path.join(Config().ReadXdebugPath(),'cachegrind.out.123'),'w')
    f.write('test')
    f.close()
    
    if Dumpdir().hasChanged():
        print "Changed"
    else:
        print "No change"
    """
