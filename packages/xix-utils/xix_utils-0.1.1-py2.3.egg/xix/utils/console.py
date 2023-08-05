"""
console.py

Linux console goodies.

Copyright (c) 2005 Drew Smathers
See LICENSE for details.

"""

# $Id: console.py 177 2005-12-20 19:59:38Z drew $

__author__ = 'Drew Smathers'
__copyright__ = '(c) 2005 Drew Smathers'
__revision__ = '$Revision: 177 $'
__license__ = 'MIT'

from xix.utils.python import setAll

globs = globals()

# ECMA-48 color codes (from console_codes manpage)
RESET                = 0    # reset all attributes to their defaults
BOLD                 = 1    # set bold
HALF_BRIGHT          = 2    # set half-bright (simulated with color on a color display)
UNDERSCRORE          = 4    # set underscore (simulated with color on a color display)
# (the colors used to simulate dim or underline are set using ESC ] ...)
BLINK                = 5    # set blink
REVERSE_VIDEO        = 7    # set reverse video
RESET_MAPPING        = 10   # reset selected mapping, display control flag,
# and toggle meta flag.
SELECT_NULL_MAPPING1 = 11   # select null mapping, set display control flag,
# reset toggle meta flag.
SELECT_NULL_MAPPING2 = 12   # DANGER! 
# select null mapping, set display control flag, set toggle meta flag. 
# (The toggle meta flag causes the high bit of a byte to be toggled
# before the mapping table translation is done.)
# 21   # set normal intensity (this is not compatible with ECMA-48)
NORMAL_INTENSITY     = 22   # set normal intensity
UNDERLINE_OFF        = 24   # underline off
BLINK_OFF            = 25   # blink off
UNSET_REVERSE_VIDEO  = 27   # reverse video off

# foreground colors
FOREGROUND = dict (
    BLACK           = 30,   # set black foreground
    RED             = 31,   # set red foreground
    GREEN           = 32,   # set green foreground
    BROWN           = 33,   # set brown foreground
    BLUE            = 34,   # set blue foreground
    MAGENTA         = 35,   # set magenta foreground
    CYAN            = 36,   # set cyan foreground
    WHITE           = 37,   # set white foreground
    DEFAULT1        = 38,   # set underscore on, set default foreground color
    DEFAULT2        = 39    # set underscore off, set default foreground color
)

# additional aliases
for k, v in FOREGROUND.items():
    globs['FG' + k] = v

# background colors
BACKGROUND = dict (
    BLACK          = 40,   # set black background
    GRED           = 41,   # set red background
    GREEN          = 42,   # set green background
    BROWN          = 43,   # set brown background
    BLUE           = 44,   # set blue background
    MAGENTA        = 45,   # set magenta background
    CYAN           = 46,   # set cyan background
    WHITE          = 47,   # set white background
    DEFAULT        = 49   # set default background color
)

# additional aliases
for k, v in BACKGROUND.items():
    globs['BG' + k] = v

class Format:

    format_on = True

    def __call__(self, message, *codes):
        return self.format(message, *codes)

    def format(self, message, *codes):
        """Format meessage give list of codes defined as globals in this module.
        
        Example usage:
         
        >>> from xix.utils.console import format
        >>> s = format('console test', FGBROWN, BGBLUE, BOLD)
        >>> s
        '\\x1b[33;44;1mconsole test\\x1b[0m'
       
        Supressing format in application:
            
        >>> format.format_on = False
        >>> s = format('console test')
        >>> s
        'console test'
        
        """
        if not self.format_on:
            return message    
        code_string = ';'.join([str(code) for code in codes])
        return '\033[%sm%s\033[%sm' % (code_string, message, RESET) 

format = Format()
   
__all__ = setAll([], locals(), 'setAll', 'k', 'v')

