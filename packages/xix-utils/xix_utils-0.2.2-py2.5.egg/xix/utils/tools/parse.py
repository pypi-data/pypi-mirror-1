__author__ = 'Drew Smathers'
__contact__ = 'andrew.smathers@turner.com'

from xix.utils.tools.options import OptionException, Option
from xix.utils.tools.options import OptionCollection
from xix.utils.tools.interfaces import IParser
from xix.utils.comp.interface import implements
import re

CONT_CHAR_PATT = re.compile(r'^[a-zA-Z_]')
VALUE_PATT = re.compile(r'"([^"]*)"')
VAR_NAME = re.compile(r'^[a-zA-Z_]\w*$')

class OptionParser:
    """Implement IParser

    >>> from zope.interface.verify import verifyClass
    >>> int(verifyClass(IParser, OptionParser))
    1
    """
    implements(IParser)

    def parse(self, text):
        pass

class OptionParserException(Exception):
    """Generic parse exception for OptionParser object. Raised
    on known exception in parse method of parser.
    """

class TextualOptionParser(OptionParser):
    """Parser for plain text configuration for options.  Plain
    text configuration provides subset of optparse API.
    
    Example:

    >>> from zope.interface.verify import verifyClass
    >>> int(verifyClass(IParser, TextualOptionParser))
    1
    """

    START = 0
    READING_OPTION = 1

    def __init__(self):
        raise NotImplementedError
    
    def parse(self, input):
        state = self.START
        # operations/queries
        nothing = self.__isnothing
        comment = self.__isacomment
        cont = self.__isacont
        start = self.__isastart
        options = OptionCollection()
        curried = None
        #
        if hasattr(input, 'readlines'):
            lines = input
        else:
            lines = input.split('\n')
        for line in lines:
            if nothing(line) or comment(line):
                continue
            elif start(line):
                if curried:
                    option = Option(**curried)
                    options.append(option)
                    curried = None
                curried = self.__build_options(line)
            elif cont(line):
                if curried is None:
                    errmsg = 'Cannot parse: %s' % line
                    raise OptionParserException, errmsg
                self.__build_options(line, curried=curried)
            else:
                errmsg = 'Cannot parse: %s' % line
                raise OptionParserException, errmsg
        if curried:
            option = Option(**curried)
            options.append(option)
        return options
                    

    def __build_options(self, line, curried=None):
        l = line.strip()
        tokens = l.split()
        if not curried:
            # one and/or two should be CLI descs
            short, long = tokens[:2]
            if not (short[0] == '-' or long[0] != '-'):
                errmsg = 'No short/long flags given'
                raise OptionParserException, errmsg
            if short[:2] == '--':
                if long[0] == '-':
                    errmsg = 'Short flag should be given before long flag'
                    raise OptionParserException, errmsg
                long = short
                args = tokens[1:]
            elif short[:1] == '-':
                if long[:2] != '--':
                    args = tokens[1:]
                    long = ''
                else:
                    args = tokens[2:]
            else:
                errmsg = 'Invalid token sequence: ', ','.join(tokens)
                raise OptionParserException, errmsg
            curried = { 'short_desc': short, 'long_desc': long }
        else:
            args = tokens
        pairs = self.__validargs(args)
        for name, value in pairs:
            curried[name] = value
        return curried
            
    def __isnothing(self, line):
        l = line.strip()
        return  l == ''
                
    def __isastart(self, line):
        l = line.strip()
        return l[0] == '-'

    def __isacomment(self, line):
        l = line.strip()
        return l == '#'

    def __isacont(self, line):
        l = line.strip()
        return CONT_CHAR_PATT.match(l) is not None

    def __isastr(self, value):
        return VALUE_PATT.match(value) is not None

    def __getvalue(self, text):
        if self.__isacont(text):
            return VALUE_PATT.match(text).groups()[0]
        else:
            return text

    def __validargs(self, args):
        try:
            pairs = [(name, self.__getvalue(value)) \
                    for name, value in [arg.split('=') for arg in args]]
            for name, value in pairs:
                if VAR_NAME.match(name) is None:
                    errmsg = 'Invlaid name in assignment: %s= ...' % name 
                    raise OptionParserException, errmsg
        except Exception, e:
            errmsg = "invalid argument structure: %s. (%s)" % (args, e)
            raise OptionParserException, errmsg
        return pairs
        

_TEST_OPTIONS_TEXTUAL = """
-s --host dest="host" default="example.com"
            help="name of host"
            
-z --zoo dest="zoo" default='atl'
   # This is a comment
            help='where animals live"

--recurring action="store_true" dest="recurring_only"
help="let it be recurring"
            
# This is a comment
            
-p --path dest="path" default="/home"
            help="the yellow brick road"
"""

def _testTextualOptionParser():
    """Example:

    #>>> parser = TextualOptionParser()
    #>>> o = parser.parse(_TEST_OPTIONS_TEXTUAL)
    #>>> print o.zoo
    #atl
    #>>> print o._data['zoo'].help
    #where animals live
    #>>> print o._data['zoo'].short_desc
    #-z
    #>>> print o._data['zoo'].long_desc
    #--zoo
    #>>> print o._data['recurring_only'].help
    #let it be recurring
    #>>> print o._data['recurring_only'].long_desc
    #--recurring
    #>>> print o._data['recurring_only'].short_desc
    #None

    >>> try:
    ...     parser = TextualOptionParser()
    ... except NotImplementedError:
    ...     print 'TextualOptionParser is not complete'
    ...
    TextualOptionParser is not complete
    """

