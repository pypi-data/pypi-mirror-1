# rest currently is:
#
# collection of resful decorators for making
# web controller function only accept specified 
# HTTP method
#
# rest module will be:
#
# ?

from xix.utils import decor

__author__ = 'Drew Smathers <drew dot smathers at gmail dot com>'
__version__ = '$Revision$'[11:-2]

class NotRestfulException(Exception):
    """Raised when method is invoked in violation to its
    restful signature.  E.g. called with GET method when
    declared as POST.
    """

class RestDecorator(object):
    """Abstract RESTful decorator
    """
    method = None

    def __init__(self, getmethod_f=None):
        self.getmethod_f = get_method_f or PostDecorator._getmethod

    def __call__(func):
        def _wrapped(*args, **kargs):
            m = self.getmethod_f(*args, **kargs)
            if m != self.method:
                raise NotRestfulException,
                    'Expected method %s, but got %s' % (self.method, m)
            return func(*args, **kargs)
        return decor.decorate(_wrapped)


    @staticmethod
    def _getmethod(*args, **kwargs): # default based on paste
        pass

class PostDecorator(RestDecorator):
    method = 'POST'


# install globals
post = PostDecorator()

# optional post initialization to change globals
def init(**decorators):
    """Redefined global get,post,put,delete,head functions
    with get method functions:

        { 'get' : my_decoratior, ... }
    """
    g = globals()
    for (func_name, func) in decorators.items():
        g[func_name] = func

