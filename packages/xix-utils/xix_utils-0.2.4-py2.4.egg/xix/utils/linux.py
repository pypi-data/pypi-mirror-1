'''
Linux-only hodge-podge utilities.

Copyright (c) 2005 Drew Smathers
See LICENSE for details.

$Id: linux.py 399 2007-01-22 01:27:13Z djfroofy $

'''

import sys
from xix.utils.comp.interface import implements
from xix.utils import console
from xix.utils.python import setAll

_islinux = sys.platform == 'linux-i386' or sys.platform == 'linux2'

if _islinux:
    def changeXtermTitle( title ):
        sys.stdout.write('%c%c]2;%s%c' % ( 0x07, 0x1b, title, 0x07 ))
else:
    def changeXtermTitle( title ):
        pass

__all__ = ['changeXtermTitle']
    
