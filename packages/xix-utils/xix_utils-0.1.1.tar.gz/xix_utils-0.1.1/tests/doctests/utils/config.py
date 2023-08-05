"""
doctests for xix.utils.config
"""

__author__ = 'Drew Smathers'
__version__ = '$Revision: 159 $'[11:-2]

from xix.utils.config import Config, ConfigLoader, ConfigFactory, configFactory
from xix.utils.config import ModuleWrapper

# pydoc unit tests

class File:
    def __init__(self, data):
        self.data = data
    def read(self):
        return self.data

class ConfigLoaderTest:
    def example_noDuplicateEntries(self):
        """
        Duplicate entries are strictly not allowed:

        >>> fd = File('''
        ... foo.bar=123
        ... foo.bar="foobar"
        ... ''')
        >>> loader = ConfigLoader()
        >>> loader.load(fd)
        Traceback (most recent call last):
        ...
        ConfigLoaderException: Duplicate entry foo.bar
        """
    def example_cannotOverrideTerminalNodes(self):
        """
        Cannot override terminal nodes:

        >>> fd = File('''
        ... foo=123
        ... foo.bar="foobar"
        ... ''')
        >>> loader = ConfigLoader()
        >>> loader.load(fd)
        Traceback (most recent call last):
        ...
        ConfigLoaderException: Duplicate entry foo.bar
        """
    def example_wellFormedFiles():
        """
        Configuration files must be well formed:

        >>> fd = File("crap here")
        >>> loader = ConfigLoader()
        >>> loader.load(fd)
        Traceback (most recent call last):
        ...
        ConfigLoaderException: Malformed line found in configuration: crap here
        """
    def example_validNodeName(self):
        """
        Configuration nodes must be valid python names:

        >>> fd = File("this.123='hello'")
        >>> loader = ConfigLoader()
        >>> loader.load(fd)
        Traceback (most recent call last):
        ...
        ConfigLoaderException: Config node 123 does not map to valid Python name
        """
    def example_valueImplicitPythonSyntax(self):
        """
        Type values are implicit by given python syntax:

        >>> fd = File("foo.bar=[1,2,3]")
        >>> loader = ConfigLoader()
        >>> cfg = loader.load(fd)
        >>> type(cfg.foo.bar)
        <type 'list'>
        """
    def example_builtinPlugins_path(self):
        """Using the builtin path plugin

        >>> fd = File("foo.bar=path('/this/is/a/path')")
        >>> loader = ConfigLoader()
        >>> cfg = loader.load(fd)
        >>> import os.path
        >>> int(os.path.sep in cfg.foo.bar)
        1
        >>> print cfg.foo.bar.replace(os.path.sep, '/')
        /this/is/a/path
        """
    def example_mustIndicateStringsWithQuotes(self):
        """
        Strings MUST be indicated with quotes (single or double):
        
        >>> fd = File("foo.bar=not good dude")
        >>> loader = ConfigLoader()
        >>> loader.load(fd)
        Traceback (most recent call last):
        ...
        ConfigLoaderException: Internal exception while trying to convert not good dude -- Cannot resolve type : not good dude.
        """
    def example_someTypesNotSupported(self):
        """
        Not all types are supported:
        
        >>> fd = File("foo.bar=type")
        >>> loader = ConfigLoader()
        >>> loader.load(fd)
        Traceback (most recent call last):
        ...
        ConfigLoaderException: Unsupported type: <type 'type'>.
        """
    def example_moduleWrapper(self):
        """
        We can also get a module wrapper ...

        >>> fd = File("foo.bar=xix.utils.string")
        >>> loader = ConfigLoader()
        >>> cfg = loader.load(fd)
        >>> from xix.utils.interfaces import IModuleWrapper
        >>> IModuleWrapper.providedBy(cfg.foo.bar)
        True
        """


def _resetConfigFactory():
    try: del configFactory.resources["test.cfg"]
    except: pass

class ConfigFactoryTest:
    """ConfigFactory unit tests
    """

    def verifySingletonInstance(self):
        """Let's make sure these tests are valid - i.e. configFactory
        is an instance of ConfigFactory:

        >>> configFactory.__class__ == ConfigFactory
        True
        """

    def getConfig(self):
        """Example usage of config API.  You should make a __appcfg__.py
        module for you package which does all the addResource shit ...

        >>> _resetConfigFactory()
        >>> from xix.utils.python import fileHere
        >>> configFactory.addResource("test.cfg", fileHere("__testcfg__.cfg"))
        >>> cfg = configFactory.getConfig("test.cfg")
        >>> cfg.my.little.test
        'Hello World'
        """

    def callAlias(self):
        """Using call instead of getConfig

        >>> _resetConfigFactory()
        >>> from xix.utils.python import fileHere
        >>> configFactory.addResource("test.cfg", fileHere("__testcfg__.cfg"))
        >>> cfg = configFactory("test.cfg")
        >>> cfg.my.little.test
        'Hello World'
        """

    def reloadConfig(self):
        """Reloading a config forces the config to be loaded again into memory.
        This will reload from file of course, which means any references to config
        object you have elsewhere may be out of sync with what's freshly loaded.

        >>> _resetConfigFactory()
        >>> from xix.utils.python import fileHere
        >>> configFactory.addResource("test.cfg", fileHere("__testcfg__.cfg"))
        >>> cfg = configFactory.getConfig("test.cfg")
        >>> cfg.my.little.test = "Shit Mate"
        >>> cfg.my.little.test
        'Shit Mate'
        >>> cfg = configFactory.reloadConfig("test.cfg")
        >>> cfg.my.little.test
        'Hello World'
        >>> cfg = configFactory.getConfig("test.cfg")
        >>> cfg.my.little.test
        'Hello World'
        """

    def addResource_url(self):
        """Adding a reource ... This is demonstrated well in other tests, but here
        goes.

        >>> _resetConfigFactory()
        >>> from xix.utils.python import fileHere
        >>> from xix.utils.interfaces import IConfig
        >>> configFactory.addResource("test.cfg", fileHere("__testcfg__.cfg"))
        >>> cfg = configFactory.getConfig("test.cfg")
        >>> IConfig.providedBy(cfg)
        True
        """
   
    def addResource_config(self):
        """Using config keyword argument:

        >>> _resetConfigFactory()
        >>> from xix.utils.python import fileHere
        >>> from xix.utils.interfaces import IConfig
        >>> cfg = Config({"blue":3.14, "red":21})
        >>> configFactory.addResource("test.cfg", config=cfg)
        >>> "test.cfg" in configFactory.loaded
        True
        >>> cfg = configFactory.getConfig("test.cfg")
        >>> IConfig.providedBy(cfg)
        True
        """

    def addResource_urlAndConfig(self):
        """Using url and config keyword arguments together:

        >>> _resetConfigFactory()
        >>> from xix.utils.python import fileHere
        >>> from xix.utils.interfaces import IConfig
        >>> cfg = Config({"blue":3.14, "red":21})
        >>> configFactory.addResource("test.cfg", url=fileHere("__testcfg__.cfg"), config=cfg)
        >>> "test.cfg" in configFactory.loaded
        True
        >>> cfg = configFactory.getConfig("test.cfg")
        >>> IConfig.providedBy(cfg)
        True
        >>> print cfg.blue
        3.14
        >>> print cfg.red
        21
        >>> cfg = configFactory.reloadConfig("test.cfg")
        >>> cfg.my.little.test
        'Hello World'
        """

