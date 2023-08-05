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
2. Object loader casting
3. Textual substitution in configuration:
    ex. 
    foo.world="World"
    foo.greeting="Hello " + $foo.world

    foo.lazy=1 + $foo.eval
    foo.eval=0
              
'''

from xix.utils.interfaces import IConfig, IConfigLoader, IConfigFactory
from xix.utils.interfaces import IModuleWrapper
from xix.utils.comp.interface import providedBy, implements, classProvides
from xix.utils.python import allexcept
from xix.utils.python import ModuleWrapper
from xix.utils.python import getCallersGlobals
import warnings
import re
import os.path

__author__ = 'Drew Smathers <drew.smathers@gmail.com>'
__version__ = '$Revision: 175 $'[11:-2]

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
        
        '''
        if name in self.__dict__["_lookup"]:
            return self.__dict__["_lookup"][name]
    def __setattr__(self, name, value):
        '''
        Example usage:

        >>> cfg = Config()
        >>> cfg.property = "test"
        >>> print cfg.property
        test
        
        '''
        self.__dict__["_lookup"][name] = value


class ConfigParser:
    '''@todo implement me - ez man
    '''
    pass
    
   
def _unixpath(path):
    return path.replace('/', os.path.sep)
    
    
class ConfigLoader:
    '''Loads configuration resource and returns a Config object.
    '''
    
    classProvides(IConfigLoader)

    plugins = {
        'path' : _unixpath,
    }
    
    def load(self, fd):
        '''
        Example usage:
        
        >>> class File:
        ...     def read(self):
        ...         return """
        ... foo.bar=123
        ... foo.baz='hello world'
        ... foo.foo.nested.pi=3.14
        ... """
        ...
        >>> fd = File()
        >>> loader = ConfigLoader()
        >>> cfg = loader.load(fd)
        >>> print cfg.foo.bar, cfg.foo.baz, cfg.foo.foo.nested.pi
        123 hello world 3.14
        '''
        cfg = Config()
        for line in (fd.read().split('\n')):
            try:
                if line[0] == "#": continue
                if line.split() == []: continue
            except: continue
            try:
                cfg_chain = line.split("=")[0]
                cfg_val   = line.split("=")[1]
                cfg_chain = cfg_chain.split(".")
                assert len(cfg_chain) > 0
            except:
                raise ConfigLoaderException("Malformed line found in configuration: %s" % line)
            try:
                cast = self._caster(cfg_val)
                cfg_val = cast(cfg_val)
            except ConfigLoaderException, cle:
                raise ConfigLoaderException(str(cle))
            except Exception, e:
                raise ConfigLoaderException("Exeception occurred in loading: " + str(e))
            for node in cfg_chain:
                if not _isvalidname(node):
                    raise ConfigLoaderException(\
                            "Config node %s does not map to valid Python name" % node);
            self._updateConfig(cfg, cfg_chain, cfg_val)
        return cfg
        
    
    def _updateConfig(self, cfg, cfg_chain, cfg_value):
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
                    cfg = getattr(cfg, node)
                else:
                    raise ConfigLoaderException("Duplicate entry %s" % name)
            else:
               if chain:
                    child = Config()                    
                    setattr(cfg, node, child)
                    cfg = child
               else:
                    setattr(cfg, node, cfg_value)

    
    def _caster(self, s):
        namespace = {}
        try:
            try:
                # TODO - This is extremely unsafe - need an rexec
                exec("tipe = type(%s)" % s, namespace, namespace)
                tipe = namespace["tipe"]
                if tipe == int or tipe == long:
                    return _IntegerCaster()
                if tipe == float:
                    return _FloatCaster()
                if tipe == str:
                    return _StringCaster()
                if tipe == bool:
                    return _BooleanCaster()
                if tipe == list:
                    return _ListCaster()
                if tipe == tuple:
                    return _TupleCaster()
                if tipe == dict:
                    return _DictionaryCaster()
            except:
                if _modulename(s): # This will go away in future versions.
                    return _ModuleWrapperCaster()
                if _plugin(s):
                    return _PluginCaster()
                raise ConfigLoaderException("Cannot resolve type : %s." % s)
        except Exception, e:
            raise ConfigLoaderException(\
                    'Internal exception while trying to convert %s -- %s' % (s, e))
        raise ConfigLoaderException('Unsupported type: %s.' % type(tipe))

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

def _modulename(name):
    modname_pattern = re.compile(r'^([a-zA-Z]\w*(\.[a-zA-Z]\w*)?)+$')
    return modname_pattern.match(name) is not None

def _plugin(strng):
    plugin_patt = re.compile(r'\s*[_a-zA-Z]+\s*\(.*\)\s*$')
    return plugin_patt.match(strng) is not None

## -- end Private utility functions
###############################################################################

###############################################################################
# -------- INTERNAL ----------  Loaders for various types ---------------------
###############################################################################


class _Caster:
    def _exec(self, val):
        ns = {}
        exec("val=%s" % val, ns, ns)
        return ns["val"]
    def __call__(self, val):
        return  self._exec(val)
    
class _IntegerCaster(_Caster):
    def __call__(self, val):
        return int(val)

class _FloatCaster(_Caster):
    def __call__(self, val):
        return float(val)

class _StringCaster(_Caster):
    def __call__(self, val):
        return str(val)[1:-1] # get rid of quotes

class _BooleanCaster(_Caster):
    def __call__(self, val):
        return "True" == val
        
class _ListCaster(_Caster):
    pass
    
class _TupleCaster(_Caster):
    pass

class _DictionaryCaster(_Caster):
    pass

class _ModuleWrapperCaster(_Caster):
    def __call__(self, val):
        return ModuleWrapper(val)

class _PluginCaster(_Caster):
    def __call__(self, val):
        ns = dict(ConfigLoader.plugins)
        ns['__val__'] = None
        exec('__val__=%s' % val, ns, ns)
        return ns['__val__']

#__all__ = allexcept("IConfig", "IConfigLoader", "IConfigFactory", 
#        "providedBy", "implements", "allexcept", "ModuleWrapper")
