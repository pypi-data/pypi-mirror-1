"""Tool options.
"""

__author__ = 'Drew Smathers'
__contact__ = 'andrew.smathers@turner.com'

from xix.utils.comp.interface import implements
from xix.utils.tools.interfaces import IOption, IOptionCollection
import re


VAR_NAME = re.compile(r'^[a-zA-Z_]\w*$')

class OptionException(Exception):
    """Exception relating to options configuration.
    """

class Option(object):
    """An option is a schema for an argument to a tool.  Schema must
    include either/both of short_desc and long_desc and most have
    a dest set.

    Example:

    >>> opt = Option('-o', '--option', dest='option', default='nothing')
    >>> print opt.short_desc, opt.long_desc, opt.dest, opt.default
    -o --option option nothing

    Option implements IOption.

    >>> from zope.interface.verify import verifyClass 
    >>> int(verifyClass(IOption, Option))
    1
    """

    implements(IOption)
    
    def __init__(self, short_desc=None, long_desc=None, dest=None, **kwargs):
        """
        @param short_desc: short description for cli flag
        @param long_desc: long descriptiong for cli flag
        @param dest: destination variable for
        @param kwargs: other keyword arguments.
        """
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.dest = dest
        self.__dict__.update(kwargs)
        self.__set_other_props()

    def __set_other_props(self):
        for attr in ('type', 'help', 'default', 'value'):
            if not hasattr(self, attr):
                setattr(self, attr, None)
        if self.type == None:
            self.type = 'str'
    
class OptionCollection(object):
    """Collection of Options.  Corresponds roughly to
    Options of optparse.
    
    Exampe Usage:
    
    >>> o1 = Option('-t', '--target', dest='target', help='our target')
    >>> o2 = Option('-c', '--candy', dest='candy', help='very sweet')
    >>> options = OptionCollection(o1, o2)
    >>> print options.target, options.candy
    None None
    
    Set options o1 and o2:

    >>> o1.value = 'moon'
    >>> o2.value = 'rocks'
    >>> print options.target, options.candy
    moon rocks

    OptionCollection implements IOptionCollection

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IOptionCollection, OptionCollection)
    1
    """

    implements(IOptionCollection)

    def __init__(self, *options):
        self.__dict__['_data'] = {} # hack ...
        self.__dict__['_datalist'] = []
        for option in options:
            self.append(option)

    def append(self, option):
        """Add an option:
        
        >>> o1 = Option('-t', '--target', dest='target', default='123')
        >>> o2 = Option('-c', '--candy', dest='candy', default='456')
        >>> options = OptionCollection(o1, o2) 
        >>> o3 = Option('-r', '--rah', dest='rah', default='zoo')
        >>> options.append(o3)
        >>> print options.target, options.candy, options.rah
        123 456 zoo
        """
        options = self._data
        if options.has_key(option.dest):
            errmsg = 'Option already defined with name "%s"'
            raise OptionException, errmsg % option.dest
        if hasattr(self, option.dest):
            errmsg = "'%s' already exists as an attribute of '%s'"\
                     "instance" % (option.dest, self.__class__.__name__)
            raise OptionException, errmsg
        if not _isaname(option.dest):
            errmsg = '"%s" is not a valid attribute name.' % option.dest
            raise OptionException, errmsg
        self._data[option.dest] = option
        self._datalist.append(option)

    def add_option(self, *args, **kwargs):
        """Example usage:

        >>> options = OptionCollection()
        >>> options.add_option('-t', dest='mytool', default='lever')
        >>> o = options._data['mytool']
        >>> print options.mytool, o.default
        lever lever
        """
        opt = Option(*args, **kwargs)
        self.append(opt)

    def __getattr__(self, name):
        """Getting normal properties should not cause problems:

        >>> options = OptionCollection()
        >>> print options._data
        {}

        Getting properties that do not exist:

        >>> try:
        ...     print options.doowap
        ... except AttributeError:
        ...     print 'doh'
        ...
        doh
        """
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        elif self._data.has_key(name):
            d = self._data
            return (d[name].value, d[name].default)[ d[name].value is None ]
        errmsg = "'%s' has no attribute '%s'" % (self.__class__.__name__, name)
        raise AttributeError, errmsg

    def __setattr__(self, name, value):
        """Setting option:
    
        >>> o1 = Option('-t', '--target', dest='target', default='123')
        >>> options = OptionCollection(o1)
        >>> options.target = "testing..."
        >>> print options.target, o1.value
        testing... testing...
        """
        if self._data.has_key(name):
            self._data[name].value = value
        else:
            setattr(self, name, value)

    def __iter__(self):
        """ Example:
        
        >>> o1 = Option('-t', '--target', dest='target', default='123')
        >>> o2 = Option('-c', '--candy', dest='candy', default='456')
        >>> options = OptionCollection(o1, o2) 
        >>> for opt in options:
        ...     print opt.dest
        ...
        target
        candy
        """
        return iter( self._datalist )
            

def _isaname(name):
    return VAR_NAME.match(name) is not None

    
def toOptParser(options):
    """return optparse OptionParser given an options collection.

    >>> o1 = Option('-t', '--target', dest='target', default='123')
    >>> o2 = Option('-m', dest='mold', help='blue stuff')
    >>> command = '-t 678 -m pink 1 2 3'
    >>> options = OptionCollection(o1, o2)
    >>> parser = toOptParser(options)
    >>> (opts, args) = parser.parse_args(command.split())
    >>> print opts.target
    678
    >>> print opts.mold
    pink
    >>> print args
    ['1', '2', '3']
    """
    import optparse
    parser = optparse.OptionParser()
    for opt in options._data.values():
        args = [None]
        kwargs = {}
        for name, value in opt.__dict__.items():
            if name == 'value':
                continue
            if name == 'type' and hasattr(opt, 'action') \
                     and opt.action in ('store_true', 'store_false'):
                continue
            if name == 'short_desc': 
                args[0] = value
            elif name == 'long_desc':
                args.append(value)
            elif name[0] != '_':
                kwargs[name] = value
        if args[0] is None:
            args = args[1:]
        parser.add_option(*args, **kwargs)
    return parser

