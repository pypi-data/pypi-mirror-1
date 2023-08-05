import os
from os.path import exists
from stat import *

from patterns.singleton import Singleton
from analyzer import Analyzer

class BaseProfile(object):
    """
    Represents a single Xdebug profile output and is used to store
    datastructures obtained from parsing the profile file
    """
    
    def __init__(self, name):
        if not exists(name):
            raise IOError, str(name)+" not found"
        self.initialize(name)
    
    def initialize(self, name):
        self.initialized = 1
        self.name = name
        self.a = Analyzer(self)
        self._loadmeta()
    
    def _loadmeta(self):
        fstat = os.stat(self.name)
        self.mtime = fstat[ST_MTIME]
        self.size = fstat[ST_SIZE]
    
    def load(self, callback = lambda x : True):
        self.a.loadbody(callback)
    
    def __getattr__(self, name):
        
        """
        if name == 'a':
            self.a = Analyzer(self)
            return self.a
        """
        
        headers = 'version', 'script', 'part', 'events'
        body = 'functions', 'main', 'summary'
        
        # Header attributes...
        if name in ('version', 'script', 'part', 'events'):
            self.a.loadheader()
            if self.__dict__.has_key(name):
                return self.__dict__[name]
            return None
        """
        # Body attributes
        elif name in ('stack', 'main', 'functions', 'functionstats', 'summary'):
            self.a.loadbody()
            if self.__dict__.has_key(name):
                return self.__dict__[name]
            del self.a
            return None
        
        else:
            raise AttributeError, 'Unable to resolve attribute: '+name'''
        """

class Profile(BaseProfile):
    """
    The singleton implementation. This is used within the GUI to save
    passing the instance around
    """
    
    __metaclass__ = Singleton
    
    def __init__(self, name = None):
        if not self.__dict__.has_key('initialized'):
            if not name is None:
                BaseProfile.__init__(self, name)

class ExistingProfile(BaseProfile):
    """
    When we already know the file exists, skip the check. This is used
    by profiles.Profiles, which knows a file already exists, having read
    the directory
    """

    def __init__(self, name):
        self.initialize(name)

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    
    Profile.deleteInstance()
    file = 'c:/srv/php.net/xdebug/cachegrind.out.2771514409'
    #file = 'c:/srv/php.net/xdebug/cachegrind.out.1195372743'
    p = Profile(file)
    
    p.load()
    print p.summary
    pp.pprint(p.__dict__)
    
    """
    #f = Dumpfile('c:/srv/php.net/xdebug/cachegrind.out.10455575')
    f = Dumpfile('c:/srv/php.net/xdebug/cachegrind.out.1195372743')
    
    #f = Dumpfile('c:/srv/php.net/xdebug/cachegrind.out.2625861897')
    
    def callback(percent):
        print "Percent done: "+str(percent)
        return 1
    
    f.a.loadheader()
    print f.version
    
    f.a.loadbody(callback)
    """
    """print "PHP Script: "+f.script
    print "Dump Time: "+str(f.mtime)
    print "Dump Size: "+str(f.size)
    print "Events: "+str(f.events)
    f.a.loadbody()
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(f.main)
    #pp.pprint(f.functions)
    print "Done"
    
    stack = []
    
    i = 0
    for fn in f.functions:
        l = len(fn['stack'])
        if l == 0:
            stack.append(fn['name'])
        else:
            slice = stack[i-l:]
            stack = stack[0:i-l]
            stack.append([fn['name'], slice])
            i -= l
        i += 1
    """
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(f.stack)
    #pp.pprint(f.functionstats)
