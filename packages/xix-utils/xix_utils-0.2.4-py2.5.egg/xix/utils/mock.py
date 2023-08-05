"""Various things for mocking objects, data streams, etc.
"""

from warnings import warn
from StringIO import StringIO

__author__ = 'Drew Smathers'
__contact__ = 'drew.smathers@gmail.com'
__version__ = '$Revision$'[11:-2]

class File:
    """File mocker (only support some operations - do not
    expect this to be a full emulation of basic file type)

    Example Usage:

    >>> t = '''Hello
    ... World
    ... '''
    >>> fd = File(t)
    >>> for line in fd:
    ...    line
    ...
    'Hello\\n'
    'World\\n'
    ''
    """

    def __init__(self, text=None, mode='r'):
        warn('File implementation is not complete...')
        self.text = text or ''
        self.lines = []
        self.channel = StringIO()
        if mode == 'r':
            self.lines = [line + '\n' for line in text.split('\n')]
            self.lines[-1] = self.lines[-1][:-1]
        # TODO wrap write with consideration for mode
        self.write = self.channel.write
        self.read = lambda : self.text
        self.readlines = lambda : self.lines
        self.__iter__ = lambda : iter(self.lines)
        
