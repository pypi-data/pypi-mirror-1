from xix.utils.comp.interface import Interface, Attribute

__author__ = 'Drew Smathers'

class IParser(Interface):
    """A text/xml parser.
    """

    def parse(input):
        """Parse input and return parsed object.
        """

class IOption(Interface):
    """A schema represenation of a tool argument.
    """

    short_desc = Attribute("""Short description flag for CLI
            """)

    long_desc = Attribute("""Long description flag for CLI
            """)

    dest = Attribute("""Destination variable name fto hold resulting value.
            """)
   
    type = Attribute("""The type of the option - default is string.
            """)

    help = Attribute("""Help string for information on the tool.
            """)

    default = Attribute("""Default value for option.
            """)

    value = Attribute("""The final value assigned to the option.
            """)

class IOptionCollection(Interface):
    """Collection of Options.  Corresponds roughly to
    Options of optparse.
    """

    def append(option):
        """Append option to collection.
        """

    def add_option(*args, **kwargs):
        """Add new option given specified arguments.
        """

    def __getattr__(name):
        """Getattribute return actual attribute of IOptionCollection
        object (__xxx__) or named option.  For example:

        options.append(Option('-s', dest='foo', default=1))
        options.foo => 1
        """

    def __setattr__(name, value):
        """If option with named with dest name is in collection, value
        on IOption instance is set to value, otherwise internal dictionary
        should be updated as normal.
        """

