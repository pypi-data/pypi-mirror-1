'''
<h1>An app Configuration variable chain container.</h1>

<p>Each configuration is simply an object with attributes (valid python names)
And attribute may be another Config instance to allow for configuration trees.
For example, the following configuration may be given:</p>

<pre>
foo.bar.baz="Hello"
foo.bar.marshyPants=[1,2,3]
foo.bar.component=xix.utils.MyComponent(address='123')
baz.module=com.foobar.impl
</pre>

<p>Which specifies the following object hierarchy:</p>

<pre>
Config(<main>)+
              |-Config(foo) +
              |   ----------|-Config(bar) +
              |   ---------- -------------|-Config(baz)=<string> "Hello"
              |   ---------- -------------|-Config(marshyPants)=<list> [1,2,3]
              |   ---------- -------------|-Config(component)=<obj> MyComponent
              |-Config(baz) +
              |   ----------|-Config(module)=<module> com.foobar.impl
</pre>
              
<p>Current Limitations.  If you choose to nest properties (which you should), you cannot
not assign a value to an intermediary node of another config chain - Hence, the
following would be invalid:</p>

<pre>
tiger=23
tiger.fighter=45
</pre>

TODO:

1. Cascading configurations
              
'''

from xix.utils.interfaces import IConfig, IConfigLoader, IConfigFactory
#from xix.utils.interfaces import IModuleWrapper
from xix.utils.comp.interface import providedBy, implements, classProvides
from xix.utils.python import allexcept
#from xix.utils.python import ModuleWrapper
from xix.utils.python import getCallersGlobals
import warnings
import re
import os.path

__author__ = 'Drew Smathers <drew.smathers@gmail.com>'
__version__ = '$Revision: 253 $'[11:-2]

sectionHeader = re.compile('^\s*(\[+)([^\[\]]*)(\]+)\s*$').search
keyValue = re.compile('^([^=]+)=(.+)$').search

class ConfigException(Exception):
    '''Raised when error directly tied to configuration occurs.
    '''

class ConfigLoaderException(Exception):
    '''Raised when error directly tied to config loading process occurs.
    '''

class Config(object):
    '''Config is a configuration variable holder
    '''
    
    implements(IConfig)
    
    def __init__(self, lookup=None):
        self.__dict__["_lookup"] = lookup or {}
        
    def __getattr__(self, name):
        '''
        Example usage:

        >>> cfg = Config({"first":"Hiro", "last":'Mimoto'})
        >>> print cfg.first, cfg.last
        Hiro Mimoto

        Using nested configs:
        
        >>> cfg = Config({"tiger":27, "lion":Config({"pride":54})})
        >>> print cfg.tiger, cfg.lion.pride
        27 54

        Bug Test:

        >>> cfg = Config()
        >>> int(cfg.__class__ == Config)
        1
        
        '''
        if name in self.__dict__["_lookup"]:
            return self.__dict__["_lookup"][name]
        elif self.__dict__.has_key(name):
            return self.__dict__[name]
            
    def __setattr__(self, name, value):
        '''
        Example usage:

        >>> cfg = Config()
        >>> cfg.property = "test"
        >>> print cfg.property
        test
        >>> int(hasattr(cfg, 'property'))
        1
        
        '''
        self.__dict__["_lookup"][name] = value
        
    def __getitem__(self, name):
        """Example usage:

        >>> cfg = Config()
        >>> cfg.property = 'test'
        >>> print cfg['property']
        test
        """
        return getattr(self, name)

    def __setitem__(self, name, value):
        """Example usage:

        >>> cfg = Config()
        >>> cfg['property'] = 'test'
        >>> print cfg.property
        test
        """
        return setattr(self, name, value)


class ConfigParser:
    '''@todo implement me - ez man
    '''
    pass
    
  
############ Builtin plugins to ConfigLoader##
def _unixpath(path):
    return path.replace('/', os.path.sep)

def _replace(name):
    _loader.append((_chain, name))
###############################################

class _StringFile:

    def __init__(self, data):
        self.data = data
        self.lines = [(line + '\n') for line in data.split('\n')]

    def read(self):
        return self.data

    def readline(self):
        if self.lines:
            return self.lines.pop(0)
        return ''

BADLINE = 'Malformed line found in configuration: %s'
    
class ConfigLoader:
    '''Loads configuration resource and returns a Config object.
    '''
    
    classProvides(IConfigLoader)

    plugins = {
        '_chain' : None, # Do not reference me directly
        '_loader' : None, # Do not reference me directly
        'path' : _unixpath,
        '_' : _replace,
    }
    
    def load(self, data):
        '''
        Example usage:
        
        >>> data = """
        ... foo.bar=123
        ... foo.baz='hello world'
        ... foo.foo.nested.pi=3.14
        ... """
        >>> loader = ConfigLoader()
        >>> cfg = loader.load(data)
        >>> print cfg.foo.bar, cfg.foo.baz, cfg.foo.foo.nested.pi
        123 hello world 3.14
        '''
        if hasattr(data, 'read'):
            fd = data
        else:
            fd = _StringFile(data)
        cfg = Config()
        self.replacement = []
        self.plugins['_loader'] = self
        chainPrefixStack = []
        line = fd.readline()
        prev = ''
        while line:
            #line = line[:-1]
            line = line.strip()
            try:
                if line[0] == "#":
                    line = fd.readline()
                    continue
                if line.split() == []:
                    line = fd.readline()
                    continue
            except:
                line = fd.readline()
                continue
            if line[-1] == '\\': # continue scanning next line
                prev = prev + line[:-1]
                line = fd.readline()
                continue
            else: # finish scanning mult lines, or single line
                line = prev + line
                prev = ''
            if keyValue(line):
                cfg_chain, cfg_val = self._handleAssignment(line, keyValue(line), _flat(chainPrefixStack))
            elif sectionHeader(line):
                cfg_chain, cfg_val = self._handleSection(line, sectionHeader(line), chainPrefixStack)
            else:
                raise ConfigLoaderException, BADLINE % line
            for node in cfg_chain:
                if not _isvalidname(node):
                    raise ConfigLoaderException(\
                            "Config node %s does not map to valid Python name" % node);
            self._updateConfig(cfg, cfg_chain, cfg_val)
            line = fd.readline()
        return cfg

    def _handleAssignment(self, line, reSearchResults, chainPrefix=[]):
        lhs = reSearchResults.groups()[0].strip()
        cfg_chain = chainPrefix + lhs.split('.')
        cfg_val = reSearchResults.groups()[1].strip()
        self._chain = cfg_chain
        if len(cfg_chain) == 0:
            raise ConfigLoaderException, BADLINE % line
        try:
            cfg_val = cast(self, cfg_val)
        except ConfigLoaderException, cle:
            raise ConfigLoaderException(str(cle))
        except Exception, e:
            raise ConfigLoaderException("Exeception occurred evaluating: " + cfg_val)
        return cfg_chain, cfg_val

    def _handleSection(self, line, reSearchResults, stack):
        head, section, tail = reSearchResults.groups()
        if len(head) != len(tail):
            raise ConfigLoaderException, BADLINE % line
        if len(head) > len(stack) + 1:
            raise ConfigLoaderException, 'Subsection does not have parent: %s' % line
        while len(stack) > len(head) - 1:
            stack.pop()    
        cfg_chain = section.split('.')
        stack.append(cfg_chain)
        return cfg_chain, None
    
    def _updateConfig(self, cfg, cfg_chain, cfg_value=None):
        chain = list(cfg_chain)
        name = '.'.join(cfg_chain)
        while chain:
            node = chain.pop(0)
            try:
                attr = getattr(cfg, node)
                if attr is None: bound = False
                else: bound = True
            except AttributeError:
                bound = False
            if bound:
                if chain and IConfig.providedBy(attr):
                    cfg = attr
                elif not cfg_value is None: 
                    # TODO - decide if we really want raise exception or allowing
                    # redefinition to make overlays easier.
                    raise ConfigLoaderException("Duplicate entry %s" % name)
            else:
               if chain or cfg_value is None: # TODO unit test for None case
                    child = Config()                    
                    setattr(cfg, node, child)
                    cfg = child
               else:
                    setattr(cfg, node, cfg_value)
    
class ConfigFactory:
    '''Factory for managing multiple named configurations.
    '''

    implements(IConfigFactory)

    def __init__(self, loader=None):
        self.loader = loader or ConfigLoader()
        self.resources = {}
        self.loaded = {}

    def getConfig(self, name=None):
        if name is None:
            warnings.warn('name argument will be required in future release')
            name = getCallersGlobals([__name__])['__name__']
        if name in self.loaded: 
            return self.loaded[name]
        self.loaded[name] = self.loader.load(open(self.resources[name]))
        return self.loaded[name]

    def __call__(self, name=None):
        return self.getConfig(name=name)

    def reloadConfig(self, name):
        assert name in self.resources, 'Must have resource URL for reload'
        del self.loaded[name]
        return self.getConfig(name)

    def addResource(self, name, url=None, config=None):
        if name in self.resources:
            raise ConfigLoaderException, 'Resource with name %s already registered' % name
        if url: self.resources[name] = url
        if config: self.loaded[name] = config

configFactory = ConfigFactory()

###############################################################################
## -- Private utility functions
    
def _isvalidname(name):
    class _klass: 
        pass
    try:
        inst = _klass()
        ns = dict(inst=inst) # <-- Not a butt!
        exec('inst.%s = 1' % name, ns, ns)
    except SyntaxError: return False
    return True

#def _modulename(name):
#    modname_pattern = re.compile(r'^([a-zA-Z]\w*(\.[a-zA-Z]\w*)?)+$')
#    return modname_pattern.match(name) is not None

def _plugin(strng):
    plugin_patt = re.compile(r'\s*[_a-zA-Z]+\s*\(.*\)\s*$')
    return plugin_patt.match(strng) is not None

def _flat(seq):
    flat = []
    for inner in seq:
        flat = flat + inner
    return flat

def cast(loader, val):
    ns = dict(loader.plugins)
    ns['__val__'] = None
    exec('__val__=%s' % val, ns, ns)
    return ns['__val__']

## -- end Private utility functions
###############################################################################

