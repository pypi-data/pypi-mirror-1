'''
string module: simple functions perhaps? not in 
standard python string module

'''
# $License$
# $Id: xstring.py 399 2007-01-22 01:27:13Z djfroofy $

import math

# Allignment 

def lalign(text, cols=20):
    """example usage:

    >>> txt = lalign('a test') + '||'
    >>> print txt
    a test              ||
    """
    padding = (0, cols-len(text))[cols > len(text)]
    return text + (' ' * padding)

def center(text, cols=20):
    """example usage:

    >>> txt = center('a test') + '||'
    >>> print txt
           a test       ||
    """
    delta = cols - len(text)
    pleft = int(math.floor(delta / 2.))
    pright = int(math.ceil(delta / 2.))
    return (' ' * pleft) + text + (' ' * pright)

def ralign(text, cols=20):
    """example usage:

    >>> txt = ralign('a test') + '||'
    >>> print txt
                  a test||
    """
    padding = (0, cols-len(text))[cols > len(text)]
    return (' ' * padding) + text

class IndentPrint:
    '''
    Handy little closure for stateful indented printing.
    '''
    def __init__(self, start=0, indent=3, space=' ', printer=None):
        self._start = start
        self._indent = indent
        self._space = space
        self._level = start
        self._print = printer or self._std_print

    @staticmethod
    def _std_print(s):
        print s

    def __call__(self, s):
        '''
        Print string s with optional indentation.

        Example:

        >>> p = IndentPrint()
        >>> p("Hello IndentPrint")
        Hello IndentPrint
        '''
        self._print((self._space * self._level) + s)
        self._indented = False

    def __rshift__(self, s):
        '''
        Print string s, indenting to the right.

        Example:

        >>> p = IndentPrint()
        >>> p >> "A"
           A
        >>> p >> "B"
              B
        >>> p >> None; p("C")
                 C
        '''
        self._level = self._level + self._indent
        if s is not None: self(s)
        self._indented = True

    def __lshift__(self, s):
        '''
        Print string s, reversing indentation.

        Example:

        >>> p = IndentPrint()
        >>> p >> "A"
           A
        >>> p >> "B"
              B
        >>> p("B")
              B
        >>> p << "C"
           C
        '''        
        if self._level > self._start:
            self._level = self._level - self._indent
        if s is not None: self(s)
        self._indented = False


iprint = IndentPrint()

def underline(msg, chr='-'):
    """Underline string msg with stream of characters to same length.

    Examplae usage:

    >>> print underline('This is a message')
    This is a message
    -----------------
    >>> print underline('This is another message', chr='*')
    This is another message
    ***********************
    """
    return msg + '\n' + chr * len(msg)

def trim( string, maxlen=100, ellipsis='...' ):
    ellipsis = ellipsis or ''
    return string[ :maxlen-len( ellipsis ) ] + \
        (ellipsis,'')[len(string) < maxlen]

# DO NOT USE THIS METHOD ... USE YOUR MODULE'S WRITER AND TRIM INSTEAD
#def prim(string, maxlen=75, ellipsis='...'):
#    write( trim( string, maxlen, ellipsis=ellipsis ))

def indent( level, marker=' ' ):
    return marker*level

def _writefunc ( output ):
    print output

def prettyPrintTree( node, marker=' - ', writefunc=_writefunc, _depth=0 ):
    '''print tree.
    Contract: node should iterable on children and
    leaves in tree should NOT be iterable.

    @param node: tree node
    @type  node: object
    @param marker: marker to prefix each level in hierarchy
    @type  marker: string
    @param writefunc: output function
    @type  writefunc: function
    '''
    try:
        writefunc( (marker * _depth) + str(node) )
        for child in node:
            prettyPrintTree( child, marker, writefunc, _depth+1 )
    except:
        pass
        
ind = indent
    
    
