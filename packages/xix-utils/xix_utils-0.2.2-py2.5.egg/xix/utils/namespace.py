

class NamespaceInvalidationException(Exception):
    """Raised if a namespace is invalidated ...
    """
    # FIXME - not implemented on all classes in this module

def updatens(ns, other):
    """Update the namespace ns with valid names from other namespace or dict
    other.
    """
    valid = ns._isvalid
    if hasattr(other, 'items') and callable(getattr(other, 'items')):
        items = other.items()
    else:
        items = ((k, getattr(other,k)) for k in dir(other))
    for (k,v) in ((k,v) for (k,v) in items if valid(k)):
        setattr(ns, k, v)
        
class Namespace(object):
    """Namespace can map any name to a value:

    >>> ns = Namespace({'test' : 4})
    >>> print ns.test
    4
    >>> ns.TEST = '123'
    >>> ns.test = 'abc'
    >>> print ns.TEST, ns.test
    123 abc
    >>> updatens(ns, {'_test' : True})
    >>> print ns.TEST, ns.test, ns._test
    123 abc True
    """

    def __init__(self, defaults=None):
        ns = defaults or {}
        updatens(self, ns)

    def _isvalid(self, name, *args):
        """implementations should overide to constrain naming style
        """
        return True

    def __setattr__(self, name, val):
        if not self._isvalid(name, val):
            raise NamespaceInvalidationException, 'invalid name for %s: %s' % (self.__class__, name)
        self.__dict__[name] = val

class VariablesNS(Namespace):
    """Python variable names such as: `hello`, `hello_world`, `helloWorld2`.
    Must be alphanumeric, begin in lowercase.  May have `_`, but not as last character.

    >>> good = "good goodNess good_ness ex123".split()
    >>> bad = "BAD _bad 12bad bad_".split()
    >>> vars = VariablesNS()
    >>> for (i, name) in enumerate(good):
    ...     setattr(vars, name, i)
    ...
    >>> print vars.good, vars.goodNess, vars.good_ness, vars.ex123
    0 1 2 3
    >>> failedct = 0
    >>> for (i, name) in enumerate(bad):
    ...     try:
    ...         setattr(vars, name, i)
    ...     except NamespaceInvalidationException:
    ...         failedct += 1
    ...
    >>> print failedct
    4
    """

    def _isvalid(self, name, *pargs):
        return (name[:1].islower()
            and name[-1:].isalnum()
            and _uq(lambda c: c.isalnum() or c == '_', name))

PythonNS = VariablesNS

class ConstantsNS(Namespace):
    """Names should match pattern [A-Z][A-Z0-9_]*

    >>> good = "GOOD AND_GOOD JDSHFJDHS1234_12 Z".split()
    >>> bad  = "_BAD BAD_ 12BAD BAD@#$%R %$#BAD_BAD12 bad Bad Bad2".split()
    >>> constants = ConstantsNS()
    >>> for (i, name) in enumerate(good):
    ...     setattr(constants, name, i)
    ...
    >>> print constants.GOOD, constants.AND_GOOD, constants.JDSHFJDHS1234_12, constants.Z
    0 1 2 3
    >>> failedct = 0
    >>> for (i, name) in enumerate(bad):
    ...     try:
    ...         setattr(constants, name, i)
    ...     except NamespaceInvalidationException:
    ...         failedct += 1
    ...
    >>> print failedct
    8
    """

    def _isvalid(self, name, *args):
        # stubbornly refucing to use a regex ;)
        return (name[:1].isupper()
            and name[-1:].isalnum()
            and _uq(lambda c: c.isupper() or c == '_' or c.isdigit(), name))

class CamelCaseNS(Namespace):
    """Namespace where all names must be strictly alphanumeric and begin in lowercase.

    >>> good = "helloWorld helloworld hello123 h123g".split()
    >>> bad  = "hello_world 12h HELLO HELLO_WORLD hello_".split()
    >>> camel = CamelCaseNS()
    >>> for (i, name) in enumerate(good):
    ...     setattr(camel, name, i)
    ...
    >>> print camel.helloWorld, camel.helloworld, camel.hello123, camel.h123g
    0 1 2 3
    >>> failedct = 0
    >>> for (i, name) in enumerate(bad):
    ...     try:
    ...         setattr(camel, name, i)
    ...     except NamespaceInvalidationException:
    ...         failedct += 1
    ...
    >>> print failedct
    5
    """

    def _isvalid(self, name, *args):
        return name[:1].islower() and name.isalnum()

class MToNNS(Namespace):
    """A many to more 1-1 mapped namespace.

    @todo testing
    """
    def __init__(self, **kwargs):
        Namespace.__init__(self, **kwargs)
        self._left = kwargs.get('left', Namespace())
        self._right = kwargs.get('right', Namespace())
        self._right_centric()
        self._mappings = kwargs.get('mappings', set())

    def _isvalid_on_init(self):
        mapped = set()
        for (l,r) in self.mappings:
            if l in mapped or l not in self._left or r not in self._right:
                return False
            mapped.add(l)
        return self._left._isvalid() and self._right._isvalid()

    def _isvalid(self, name, *args):
        # Tired .... FIXME
        #mapping = (l,r) = args[0]
        if mapping in self._mappings:
            return False
        for alpha in (a for (a,_) in self.mappings):
            if a == l:
                return False
        return True

    def _validate(self, name, *args):
        if not self._isvalid(name, *args):
            raise NamespaceInvalidationException

    def __lshift__(self, mapping):
        self._validate(self, )

    def updateLeft(self, ns):
        self._left.update(ns)

    def updateRight(self, ns):
        self._right.update(ns)

    def _set_rightcentric(self, yn):
        self._right_centric = True

    def _get_rightcentric(self):
        return self._right_centric

    def _get_left(self):
        return self._left

    def _get_right(self):
        return self._right

    rightCentric = property(_get_rightcentric, _set_rightcentric)
    left = property(_get_left)
    right = property(_get_right)


def _is1to1(mapping, mappings):
    """given a 2-tuple mapping (a->b) where a not in seta::Set and b<-(setb::Set)
    seta + {a} maps 1-1 with setb
    """
    return mapping not in mappings

def _uq(p, l): # quick and dirty short-circuiting universal quantification
    """
    allTrue p []     = True
    allTrue p (x:xs)
        | p x       = x : allTrue p xs
        | otherise  = False
    """
    for e in l:
        if not p(e):
            return False
    return True

