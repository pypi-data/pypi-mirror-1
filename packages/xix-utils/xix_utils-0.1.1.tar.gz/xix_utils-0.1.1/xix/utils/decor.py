'''
Some simple examples of decorators for python 2.4.

$Id: decor.py 177 2005-12-20 19:59:38Z drew $
'''

from xix.utils.python import allexcept
import time, inspect

__revision__ = '$Id: decor.py 177 2005-12-20 19:59:38Z drew $'

__author__  = 'Drew Smathers <drew.smathers@gmail.com>'
__version__ = '$Revision: 177 $'[11:-2]
__copyright__ = 'Copyright (C) 2005, Drew Smathers'

def timedfunction(function):
    '''This decorator time's calls to function and prints
    to standard out.
    '''
    def wrapper(*args, **kwargs):
        before = time.time()
        result = function(*args, **kwargs)
        after = time.time()
        print '%s took %f s to complete' % \
            (function.__name__, after - before)
        return result
    # We want the wrapper (which will replace the wrappee)
    # to be transparent as much as possible.
    wrapper.__dict__.update(function.__dict__)
    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper

##########################################################################
#       Curryable functions, methods
##########################################################################
    
class CannotCurryException(Exception):
    '''
    Raise when trying to build a curryable function with mixed argument
    dimensions (keyword and positional)
    '''
    pass
# we can build a decorator that makes a function curryable 
    
def curryable(function):
    '''My magnus opus of decorators ;)
    This decorator makes the wrapped function curryable - with
    positional or keyword arguments only - no mixing folks.
    '''
    class _CurriedFunction:        
        def __init__(self, function, pargs=None, kwargs=None, nargs=None, posonly=False):
            self._function = function
            self._nargs = nargs
            if posonly or pargs:
                self._curried = pargs or []
                self._posonly = True
            else:
                self._curried = kwargs or {}
                self._posonly = False
            if self._nargs is None:
                self._nargs = len(inspect.getargspec(self._function)[0]) - \
                    (0,1)[inspect.ismethod(self._function)]
                
        def __call__(self, *pargs, **kwargs):
            if self._posonly and kwargs:
                raise TypeError, "This curryable instance accepts only positional arguments"
            if not self._posonly and pargs:
                raise TypeError, "This curryable instance accepts only keyword arguments"
            if (self._posonly):
                curried = self._curried + list(pargs)
                if len(curried) == self._nargs:
                    return self._function(*tuple(curried))
                elif len(curried) > self._nargs:
                    raise TypeError, ("curryable accepts at most %d positional arguments (%d given)" %
                        (self._nargs - len(self._curried), len(pargs)))
                else:
                    new = _CurriedFunction(self._function, pargs=curried, nargs=self._nargs)
                    return new
            else:
                curried = dict(self._curried)
                curried.update(kwargs)
                if len(curried) == self._nargs:
                    return self._function(**dict(curried))
                elif len(curried) > self._nargs:
                    raise TypeError, ("curryable accepts at most %d keyword arguments (%d given)" %
                        (self._nargs - len(self._curried), len(pargs)))
                else:
                    new = _CurriedFunction(self._function, kwargs=curried, nargs=self._nargs)
                    return new
                
    def wrapper(*args, **kwargs):
        if args and kwargs:
            raise CannotCurryException, "Curryable functions can contain only positional " +\
                "or keyword arguments (not both)"
        if args: curried = _CurriedFunction(function, posonly=True)
        else: curried = _CurriedFunction(function, posonly=False)
        return curried(*args, **kwargs)
    wrapper.__dict__.update(function.__dict__)
    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper

#__all__ = allexcept('time', 'inspect', 'allexcept')

