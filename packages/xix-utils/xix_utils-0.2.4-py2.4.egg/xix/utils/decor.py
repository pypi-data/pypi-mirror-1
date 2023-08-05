'''
Some simple examples of decorators for python 2.4.

$Id: decor.py 443 2007-08-01 18:47:38Z djfroofy $
'''

from xix.utils.python import Curried
import time, inspect
import warnings

import sys

__revision__ = '$Id: decor.py 443 2007-08-01 18:47:38Z djfroofy $'

__author__  = 'Drew Smathers <drew.smathers@gmail.com>'
__version__ = '$Revision: 443 $'[11:-2]
__copyright__ = 'Copyright (C) 2005, Drew Smathers'


def decorate(wrapper, func):
    #warnings.warn('_wrapup is deprecated. '\
    #        'Please decorate method with decor.decorate instead.')
    wrapper.__dict__.update(func.__dict__)
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper

# decorate function Adapted from pylons.decorator:


# XXX
#def decorator(func):
#    """A decorator 'decorator' - sets __dict__, __doc__, and
#    __name__ of decorator to decorated function's.
#    """
#    def wrapper(*args, **kargs): # idepodent
#        return func(*args, **kargs)
#    wrapper.__dict__.update(func.__dict__)
#    wrapper.__doc__ = func.__doc__
#    wrapper.__name__ = func.__name__
#    return wrapper

_wrapup = decorate

def curryable(func):
    """WARNING: This is broken.
    
    curryable wrapper - syntax suger for CurriedCallable.

    Example Usage:

    >>> @curryable
    ... def something(a, b, c, d=23, e=32):
    ...    return a, b, c, d, e
    ...
    >>> curried = something()
    >>> curried = something(d=56)
    
    #>>> print curried(1,2,3)
    #(1, 2, 3, 56, 32)
    """
    def wrapper(*args, **kwargs):
        import warnings
        warnings.warn('curryable decorator is broken - do not use')
        #print 'wrapper called'
        curried = Curried(func)
        return curried(*args, **kwargs)
    return _wrapup(wrapper, func)

def noraise(out=None):
    """Do not raise any exceptions ... or event report [evil laugh].  Of course
    you should likely use only in test code ...

    Example usage:

    >>> @noraise()
    ... def stupid(a, b, c=4):
    ...     print a + b + c
    ...     raise Exception
    ...
    >>> stupid(1, 2, c=5)
    8

    >>> import sys
    >>> @noraise(out=sys.stdout)
    ... def err():
    ...     raise Exception, 'bummer'
    ...
    >>> err()
    bummer

    """
    def decor(func):
        def wrapper(*pargs, **kwargs):
            try:
                return func(*pargs, **kwargs)
            except Exception, e:
                if out:
                    print >> out, e
                return
        return _wrapup(wrapper, func)
    return decor


