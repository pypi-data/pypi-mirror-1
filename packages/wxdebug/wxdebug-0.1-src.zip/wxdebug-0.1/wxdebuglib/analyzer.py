import re, math

class AnalyzerError(Exception):
    pass

class BadXdebugFile(AnalyzerError):
    pass

class BadFunctionEntry(AnalyzerError):
    pass

class Analyzer:
    """
    Responsible for parsing and initial analysis of the Xdebug profile
    dump file - analysis means building a useful data structure from the parsed
    results.
    
    Makes a distinction between the profile "header" (which can be read quickly
    and contains useful summary information about the profile (e.g. which PHP
    script it came from) and the "body", which requires significant time to parse,
    depending on size. Some callers may just want the header.
    """
    
    def __init__(self, profile):
        self.profile = profile
        
        # TODO - make copy of file first - could be updated
        # be Xdebug while reading
        
        self._initialize()
        
    def _initialize(self):
        
        self.hasheader = 0
        self.hasbody = 0
        self.percentloaded = 0
        
        for attr in 'hasheader', 'hasbody', 'percentloaded':
            self.__dict__[attr] = 0
        
        for attr in 'summary', 'main', 'functions', 'stack':
            if self.profile.__dict__.has_key(attr):
                del self.profile.__dict__[attr]
        
        self._initParseStates()
    
    def _initParseStates(self):
        self.states = {}
        for cls in Accept, Function, CalledFunction, Summary, Main, MainCalledFunction:
            self.states[cls.__name__.lower()] = cls(self)
    
    def loadheader(self):
        if self.hasheader: return
        
        fh = file(self.profile.name)
        
        lineno = 0
        g = lambda m: m.group(1)
        h = {}
        h[0] = ('version', g, 'version')
        h[1] = ('cmd', g, 'script')
        h[2] = ('part', g, 'part')
        h[4] = ('events', lambda m: m.group(1).split(' '), 'events')
        
        while 1:
            line = fh.readline()
            
            if h.has_key(lineno):
                (header, g, attr) = h[lineno]
                
                m = self.matchheader(header, line)
                
                if not m:
                    raise BadXdebugFile, "Failed to locate '"+header+":' in xdebug file: "+self.profile.name
                
                self.profile.__setattr__(attr,g(m))
            
            if lineno == 4:
                break
            
            lineno += 1
        
        fh.close()
        
        self.hasheader = 1
    
    def loadbody(self, callback = lambda x : True):
        
        if self.hasbody: return
        
        if not self.hasheader: self.loadheader()
        
        # Set the initial parsing state
        state = self.states['accept']
        
        self.profile.functions = []
        
        fh = file(self.profile.name)
        
        lineno = 0
        while 1:
            line = fh.readline()
            
            # Headers start after line 4
            if lineno < 5:
                lineno += 1
                continue
            
            # End of file
            if not line:
                self.completestack()
                callback(100)
                break
            
            # States return another state after processing a line
            state = state.process(line)
            
            # 12 is a guessed average line length for an Xdebug file
            percentloaded = math.floor(((lineno * 12.0) / self.profile.size) * 100)
            if percentloaded > 99: percentloaded = 99
            
            if (percentloaded - self.percentloaded) > 2:
                self.percentloaded = percentloaded
                if not callback(percentloaded): return
            
            lineno += 1
        
        if not self.profile.__dict__.has_key('summary'):
            raise BadXdebugFile, "Failed to locate 'summary:' in xdebug file: "+self.profile.name
        
        if not self.profile.__dict__.has_key('main'):
            raise BadXdebugFile, "Failed to locate main function in xdebug file: "+self.profile.name
        
        fh.close()
        
        self.hasbody = 1
    
    def matchheader(self, name, line):
        p = re.compile("^"+name+": (.+)\n$")
        return p.match(line)
    
    def recordmainentry(self, function):
        if not self.profile.__dict__.has_key('main'):
            self.profile.main = {}
        self.profile.main = function
    
    def recordmaindetail(self, function):
        self.profile.main.update(function)
        
        self.checkfunctionstatsexists('{main}')
        self.profile.functionstats['{main}']['selft'] += int(function['time'])
        self.profile.functionstats['{main}']['script'] = self.profile.main['script']
    
    def recordmaincalledfunction(self, function):
        self.profile.main['stack'].append(function)
        
        self.calledfnstats(function)
    
    def recordfunction(self, function):
        if not self.profile.__dict__.has_key('functions'):
            self.profile.functions = []
        self.profile.functions.append(function)
        
        self.checkfunctionstatsexists(function['name'])
        self.profile.functionstats[function['name']]['selft'] += int(function['time'])
        self.profile.functionstats[function['name']]['script'] = function['script']
    
    def recordcalledfunction(self, function):
        self.profile.functions[len(self.profile.functions)-1]['stack'].append(function)
        
        self.calledfnstats(function)
    
    def calledfnstats(self, function):
        self.checkfunctionstatsexists(function['name'])
        self.profile.functionstats[function['name']]['calls'] += 1
        self.profile.functionstats[function['name']]['cumt'] += int(function['time'])
    
    def checkfunctionstatsexists(self, name):
        if not self.profile.__dict__.has_key('functionstats'):
            self.profile.functionstats = {}
        if not self.profile.functionstats.has_key(name):
            self.profile.functionstats[name] = {'calls':0,'selft':0,'cumt':0,'script':''}
    
    # Called whenever we've seen a complete function (with cfns if any)
    def buildstack(self):
        if not self.profile.__dict__.has_key('stack'):
            self.profile.stack = []
        
        i = 0
        for fn in self.profile.functions:
            
            l = len(fn['stack'])
            
            if l == 0: self.profile.stack.append(fn)
            
            else:
                slice = self.profile.stack[i-l:]
                self.profile.stack = self.profile.stack[0:i-l]
                self.profile.stack.append([fn, slice])
                i -= l
            i += 1
        
        self.profile.functions = []
    
    def completestack(self):
        root  = {   'lineno': 0,
                    'name': self.profile.script,
                    'script': self.profile.script,
                    'time':self.profile.summary,
                    'stack': []
                }
                
        maincall = {    'calls': ('1', '0', '0'),
                        'lineno': '0',
                        'name': '{main}',
                        'time': self.profile.summary}
        root['stack'] += [maincall]
        root['stack'] += self.profile.main['stack']
        
        try:
            self.profile.stack = [root,[[self.profile.main, self.profile.stack]]]
        except:
            # If it's a profile where nothing happened (no PHP fn calls)...
            self.profile.stack = []

# TODO - for performance, eliminate regexes - overkill for problem

# Function location pattern
flp = re.compile("^fl=(.+)\n$")
# Function name pattern
fnp = re.compile("^fn=(.+)\n$")
# Lineno and time pattern
ltp = re.compile("^([0-9]+) ([0-9]+) ?([0-9]+)?\n$")
# Called function pattern
cfp = re.compile("^cfn=(.+)\n$")
# Called function calls pattern
cfcp = re.compile("^calls=([0-9]+) ([0-9]+) ([0-9]+)\n$")
# Summary pattern
sp = re.compile("^summary: (.+)\n$")

class State:
    def __init__(self, analyzer):
        self.a = analyzer
    
    def process(self, line):
        raise BadXdebugFile, "Unexpected input in dump file [line "+str(self.a.lineno)+"]: "+line
    
    def blankline(caller, line):
        if not line.lstrip():
            return True
        return False
    
class Accept(State):
    
    def process(self, line):
        
        if self.blankline(line):
            return self
        
        m = flp.match(line)
        if m:
            self.a.states['function'].start(m.group(1))
            return self.a.states['function']
        
        State.process(self, line)

class Function(State):
    
    def __init__(self, analyzer):
        State.__init__(self, analyzer)
        self.resetfunction()
    
    def resetfunction(self): 
        self.function = {}
        self.function['stack'] = []
    
    def checkfunction(self):
        ck = lambda k : self.function.has_key(k)
        if not ck('lineno') or not ck('name') or not ck('time'):
            raise BadFunctionEntry, "Function entry not complete [seen on line "+str(self.a.lineno)+"]: "+str(self.function)
    
    def start(self, script):
        self.function = {}
        self.function['script'] = script
        self.function['stack'] = []
    
    def end(self):
        self.checkfunction()
        self.a.recordfunction(self.function)
        self.resetfunction()
    
    def process(self, line):
        
        m = fnp.match(line)
        if m:
            
            self.function['name'] = m.group(1)
            
            if m.group(1) == '{main}':
                self.a.recordmainentry(self.function)
                self.resetfunction()
                return self.a.states['summary']
            else:
                return self
        
        m = ltp.match(line)
        if m:
            return self.storelt(m.group(1),m.group(2))
        
        if self.blankline(line):
            self.end()
            self.a.buildstack()
            return self.a.states['accept']
        
        m = cfp.match(line)
        if m:
            return self.storecf('calledfunction',m.group(1))
        
        State.process(self, line)
    
    def storelt(self, lineno, time):
        self.function['lineno'] = lineno
        self.function['time'] = time
        return self
    
    def storecf(self, state, function):
        self.end()
        self.a.states[state].start(function)
        return self.a.states[state]
        
class CalledFunction(Function):
    
    def __init__(self, analyzer):
        State.__init__(self, analyzer)
        self.function = {}
    
    def start(self, name):
        self.function = {}
        self.function['name'] = name
    
    def end(self):
        self.checkfunction()
        self.a.recordcalledfunction(self.function)
        self.function = {}
    
    def process(self, line):
        
        m = cfcp.match(line)
        if m:
            self.function['calls'] = m.groups()
            return self
        
        m = ltp.match(line)
        if m:
            return self.storelt(m.group(1),m.group(2))
        
        m = cfp.match(line)
        if m:
            return self.storecf('calledfunction',m.group(1))
        
        if self.blankline(line):
            self.end()
            self.a.buildstack()
            return self.a.states['accept']
        
        State.process(self, line)

class Summary(State):
    
    def process(self, line):
        
        if self.blankline(line):
            return self;
        
        m = sp.match(line)
        if m:
            self.a.profile.summary = m.group(1)
            self.a.states['main'].start()
            return self.a.states['main']
        
        State.process(self, line)

class Main(Function):
    
    def start(self):
        self.function = {}
        self.function['stack'] = []
    
    def end(self):
        self.a.recordmaindetail(self.function)
        self.function = {}
    
    def process(self, line):
        
        if self.blankline(line):
            return self
        
        m = ltp.match(line)
        if m:
            return self.storelt(m.group(1),m.group(2))
        
        m = cfp.match(line)
        if m:
            return self.storecf('maincalledfunction',m.group(1))
        
        State.process(self, line)

class MainCalledFunction(CalledFunction):
    
    def end(self):
        self.checkfunction()
        self.a.recordmaincalledfunction(self.function)
        self.function = {}
    
    def storecf(self, state, function):
        self.end()
        self.a.states['maincalledfunction'].start(function)
        return self.a.states['maincalledfunction']

if __name__ == '__main__':
    
    import os.path
    print os.path.dirname(os.path.realpath(__file__))
    
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    
    class Test(object):
        pass
    
    p = Test()
    p.name = 'c:/srv/php.net/xdebug/cachegrind.out.1195372743'
    #p.name = 'c:/srv/php.net/xdebug/cachegrind.out.2771514409'
    p.size = 10
    a = Analyzer(p)
    
    a.loadheader()
    
    #pp.pprint(p.__dict__)
    
    a.loadbody()
    
    #pp.pprint(p.__dict__)
