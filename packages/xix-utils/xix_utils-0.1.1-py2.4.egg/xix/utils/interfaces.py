from xix.utils.comp.interface import Interface, Attribute

__author__ = 'Drew Smathers'
__version__ = '$Revision: 182 $'[11:-2]

##########################################################################
# Application data store interfaces (Future)
##########################################################################

class IDataStoreNode(Interface):
    """This interface is for (potential) future use. Currently it
    is not used in xix.utils.
    """

    name = Attribute("""
            Relative name of this node""")

    children = Attribute("""
            List of children or None if this is a leaf""")

    data = Attribute("""
            Data pertaining to node or None is this is _not_ a leaf""")
        
class IDataStore(Interface):
    """DataStore interface
    """
    def addNode(node=None, parent=None, path=None, recurse=True):
        """Add DataStoreNode descibed by path, or as child to parent to 
        this dataStore. 
        
        Nota Bene: parent and path should be mutually exclusive.

        @param node: a DataStoreNode
        @type  node: IDataStore
        @param parent: parent DataStoreNode to add node to as new child
        @type  parent: IDataStoreNode
        @param path: Path to add node to.
        @type  path: string
        @param recurse: recursively create nodes for given path if they
            do not already exist
        @type  recurse: boolean
        @raises DataStoreException: on error
        @raises TypeError: if arguments supplied incorrectly
        """
    def load(path):
        """Lookup node given path.  path argumented may also be interpretted
        as a key for lookup.

        @param path: Path to add node to.
        @type  path: string
        @return a DataStoreNode
        @rtype IDataStoreNode
        """
        

##########################################################################
# Configuration-specific interfaces
##########################################################################
        
class IConfig(Interface):
    """Application configuration container
    """
    def __getattr__(configKey):
        """Return value of configifuration key.
        Example: config.verboseLogging -> True

        @param configKey: configuration key
        @type  configKey: string
        @return a configuration value
        @rtype  object
        """

class IConfigParser(Interface):
    """A Config parser.
    """
    def parse(s):
        """Parse a string s, returning a Config instance.

        @param s: string to parse
        @type  s: string
        @return: IConfig provider
        @rtype: IConfig
        """

class IConfigLoader(Interface):
    """ConfigLoader loads a configuration from a datasource.
    """
    def load(src):
        """load configuration from datasource src. Returns a Config instance.

        @param src: datasource where configuration resides
        @type  src: IDataStoreNode
        @return: IConfig provider
        @rtype: IConfig
        """

class IConfigFactory(Interface):
    """Configuration Factory for loading application configuration containers
    """
    def getConfig(name):
        """Return configuration with name name or default configuration

        @param name: name of configuration
        @type  name: string
        @return: IConfig provider
        @rtype: IConfig
        """
    def addResource(name, url):
        """Add a resource used by loader with name and url.

        @param name: symbolic name of resource
        @type  name: string
        @param  url: url of the resource
        @type   url: string
        """

##########################################################################
# Python language related interfaces
##########################################################################
        
class IModuleWrapper(Interface):
    """ModuleWrapper contains a string reference to a python module, such as
    xix.utils.string and methods for loading components of the module into the
    caller's global namespace.
    """
    
    moduleName = Attribute("""
            The name of wrapped module (ex. xix.utils.string)""")
    
    def importModule():
        """Import the module into the caller's global namespace.
        """
    def importNames(*names):
        """Import all names from module given by positional arguments into caller's
        global namespace.
        """
    def importAll():
        """Import all visible names from module into caller's global namespace.
        """

##########################################################################
# Rule interfaces
##########################################################################

class IRule(Interface):
    """Rule interface.  A rule is closure which performs validation based
    on arguments supplied.  A rule may be statefule.
    """

    def __call__(*pargs, **kwargs):
        """ Rules return True if validation based on arguments/state passes, False otherwise.
        
        @param pargs positional arguments for validation
        @param kwargs keyword arguments for validation
        @return True if all rules pass, False otherwise
        """
class IRuleChain(Interface):
    """RuleChain interface.  A rule chain acts as an aggregation of several rules.
    RuleChains pass only if all rules in the chain pass.
    """

    rules = Attribute("""Chain of rules.""")

    def __call__(*pargs, **kwargs):
        """Validate rules.  Return True if all rules pass, false otherwise.

        @param pargs positional arguments for validation
        @param kwargs keyword arguments for validation
        @return True if all rules pass, False otherwise
        """
     
##########################################################################
# Diff interfaces
##########################################################################

class IDiff(Interface):
    """A diff represents differences between a source and target sequence of objects.
    It is up to the application using this library to compute the diff object - 
    or object that adapts this interface

    same: tuple of objects that are same between the source and target sequences
    missing: tuple of objects that are in source sequence but not in target sequence
    added: tuple of objects that are in target sequence but not in source sequence
    """
    
    missing = Attribute("""Tuple of objects in target sequence but not in 
            source sequence""")

    added = Attribute("""Tuple of objects in source sequence but not in
            target sequence""")

    same = Attribute("""Tuple of objects in both source and target
            sequences""")

class IDiffFactory(Interface):
    """DiffFactory instances generate IDiff providers given source and target
    objects to compare.
    """

    def diff(source, target, **kwargs):
        """Generate IDiff provider given source and target objects and optional
        keyword arguments.
        """

###############################################################################
# Binding interfaces
###############################################################################

class IBindingRequest(Interface):
        """IBindingRequest providers represent request for binding that
        has a name to bind and creator to bind and initialize component when needed.
        """

        name = Attribute("""name to bind instances to.""")
        
        creator = Attribute("""creator callable to return object bindings""")
        
        shared = Attribute("""shared flag - True => share single or """ \
                """bundled instances.""")
        
        bundlect = Attribute(
                """Bundle count if shared - default is 1 for """ \
                """singleton sharing""") 
        
        maxcount = Attribute("""Max instantiation count if not shared""")
        
        initargs = Attribute(
                """Initialization positional args to creator""") 
        
        initkwargs = Attribute(
                """Initialization key-word args to creator""")
        
        stack = Attribute(
                """Rotating bindings stack""")
        
        createdct = Attribute(
                """Number of bindings created""")

 
class IBindingFactory(Interface):
    """IBindingFactory providers provide method 'bind` which can be
    called with an IBindingRequest to get an object instance.
    """

    def bind(bindingRequest):
        """Given a bindingRequest, return an object instance or
        raise an Exception if binding cannot be created.

        @param bindingRequest: IBindingRequest provider
        @raises Exception: if binding cannot be created.
        """

###############################################################################
# code interfaces
###############################################################################

class ICodeRunner(Interface):
    """ICodeRunner providers take code and 'run`.  The meaning of
    run and the meanind of code is left as an excercise to the reader.
    """

    def run(code):
        """run some code

        @param code: code to run.
        """

###############################################################################
# adoc interfaces
###############################################################################

class IDocTestElement(Interface):
    """A doctest element is the smallest granual of a doctest.
    """

class IDocTestUnit(Interface):
    """A granual is a segrated ordered sequence of IDocTestElements.
    """

class IDocTestLineup(IDocTestUnit):
    """A doctest lineup is an ordered sequence of IDocTestUnits. Note:
    IDocTestLineups are also IDocTestUnits.
    A whole doc test - single docstring for method, function, class etc.
    """
    
    units = Attribute("""list of units belonging to this lineup
            """)
    identifier = Attribute("""An identifier is contextual and, given
        the proper context, tells us the semantics behind this lineup. For
        example, we may identify an execution lineup as 'executable`
        """)

class IInterpreterSession(IDocTestLineup):
    """An interpretter session is a special session that can
    whose contents can be sent to an ICodeRunner provider.
    """

    interpreter = Attribute("""ICodeRunner provider to execute
        session code.
        """)


