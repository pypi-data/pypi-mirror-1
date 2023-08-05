'''
Linux-only hodge-podge utilities.

Copyright (c) 2005 Drew Smathers
See LICENSE for details.

$Id: linux.py 159 2005-12-02 20:35:19Z drew $

'''

import sys
from xix.utils.comp.interface import implements
from xix.utils.aspout import registerInternalName, streams, IFormatter
from xix.utils import console
from xix.utils.python import setAll

registerInternalName(__name__)

_islinux = sys.platform == 'linux-i386' or sys.platform == 'linux2'

if _islinux:
    def changeXtermTitle( title ):
        sys.stdout.write('%c%c]2;%s%c' % ( 0x07, 0x1b, title, 0x07 ))
else:
    def changeXtermTitle( title ):
        pass

class ConsoleColorFormatter:
    '''
    For VT Terminals with color formatting capabilities.
    '''

    implements( IFormatter )

    formats = {
        streams.OUT     : (console.FGWHITE,),
        streams.ERR     : (console.FGRED,     console.BOLD,   console.BGBLACK),
        streams.WARN    : (console.FGMAGENTA, console.BGBLACK),
        streams.DEBUG   : (console.FGCYAN,),
        streams.VERBOSE : (console.FGCYAN,    console.BGBLACK),
        streams.SILLY   : (console.FGGREEN,   console.BGBLACK),
        'UNKNOWN'       : (console.FGBROWN,   console.HALF_BRIGHT)
    }

    def _format_linux( self, msg, stream=streams.OUT, *pargs, **kwargs ):
        try:
            return console.format( msg, *self.formats[stream] )
        except KeyError:
            return console.format( msg, *self.formats['UNKNOWN'] )

    def _format_other( self, msg, stream=streams.OUT, *pargs, **kwargs ):
        return msg
        
if _islinux:
    ConsoleColorFormatter.format = ConsoleColorFormatter._format_linux
else:
    ConsoleColorFormatter.format = ConsoleColorFormatter._format_other

console_color_formatter = ConsoleColorFormatter()
    
__all__ = setAll([], locals(), 'setAll', 'registerInternalName', 'streams',
        'IFormatter', 'implements', 'sys', 'os', 'console')
