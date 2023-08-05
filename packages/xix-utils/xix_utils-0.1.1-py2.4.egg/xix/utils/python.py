"""
python.py

Python-specific utilities for python modules.

Copyright (c) 2005 Drew Smathers
See LICENSE for details.

"""

# $Id: python.py 159 2005-12-02 20:35:19Z drew $

__author__ = 'Drew Smathers'
__copyright__ = '(c) 2005 Drew Smathers'
__version__ = '$Revision: 159 $'[11:-2]
__license__ = 'MIT'

import os, inspect
from interfaces import IModuleWrapper
from comp.interface import implements
import warnings

# General aliases
pj = os.path.join

# WARNING setAll has been deprecated ... use allexcept instead
def setAll(all, locals, *exclude):
    """
    Convenience method for use at end of module to set components
    of modules.
    
    @param all: __all__
    @type  all: list
    @param locals: keys in locals of calling module
    @type  locals: list
    @param exclude: names to excude
    @type  exclude: string
    @deprecated use allexcept instead
    """
    for local in locals:
        if (local not in exclude) and local[0] != '_':
            all.append(local)
    return all

def _setAll(all, locals, *exclude):
    for local in locals:
        if (local not in exclude) and local[0] != '_':
            all.append(local)
    return all

def getCallersGlobals( internal_ns=None ):
    """
    Get globals of caller.

    @param internal_ns: names to ignore in stack search
    @return globals dictionary of caller
    """
    intns = internal_ns or []
    intns = list(intns)
    if __name__ not in intns: intns.append(__name__)
    callers_frame = None
    try:
        callers_frame = inspect.stack()[1][0]
        loop_counter = 2
        while callers_frame.f_globals['__name__'] in intns:
            del callers_frame
            callers_frame = inspect.stack()[loop_counter][0]
            loop_counter += 1
            if loop_counter == 128: break # someone's messing with us!
        globs = callers_frame.f_globals
        return globs
    finally: 
        try: del callers_frame # callers_frame may not be in ns before raise
        except UnboundLocalError: pass

def getCallersLocals( internal_ns=None ):
    """
    Get locals of caller.

    @param internal_ns: names to ignore in stack search
    @return locals dictionary of caller
    """
    intns = internal_ns or []
    intns = list(intns)
    if __name__ not in intns: intns.append(__name__)
    callers_frame = None
    try:
        callers_frame = inspect.stack()[1][0]
        loop_counter = 2
        while callers_frame.f_globals['__name__'] in intns:
            del callers_frame
            callers_frame = inspect.stack()[loop_counter][0]
            loop_counter += 1
            if loop_counter == 128: break # someone's messing with us!
        locs = callers_frame.f_locals
        return locs
    finally: 
        del callers_frame        

def _getCallerLocals():
    callers_frame = None
    try:
        callers_frame = inspect.stack()[1][0]
        loop_counter = 2
        while callers_frame.f_globals['__name__'] == __name__:
            del callers_frame
            callers_frame = inspect.stack()[loop_counter][0]
            loop_counter += 1
            if loop_counter == 128: break # someone's messing with us!
        return callers_frame.f_locals 
    finally: 
        del callers_frame

def allexcept(*exclude):
    """Return __all__ list containing everything in locals of callers except
    names indicated in exclude.
    
    Note: __all__ list defined for a module indicate what will be imported by:

    <pre>
    from mymodule import *
    </pre>

    @param exclude: names to exclude in __all__
    """
    warnings.warn("allexcept will be deprecated in future version of xix.utils")
    return _setAll([], _getCallerLocals(), *exclude)

def fileHere( filename ):
    """Get absolute path of filename in same directory as source file
    of calling module.

    @param filename: relative path of file
    @return absolute path of file
    """
    warnings.warn("fileHere is deprecated")
    src_file = getCallersGlobals([__name__])['__file__']
    return src_file[:-len(src_file.split(os.path.sep)[-1:][0])]+filename 

class ModuleWrapper:
    """Wrapper for python module with import methods.

    WARNING: loading into locals namespace may not work.

    @see IModuleWrapper
    """
    implements(IModuleWrapper)

    def __init__(self, moduleName):
        warnings.warn("ModuleWrapper is deprecated")
        self.moduleName = moduleName
    
    def importAll(self, locals=False):
        ns = self._getNS(locals)
        exec('from ' + self.moduleName + ' import *', ns, ns)

    def importModule(self, locals=False):
        ns = self._getNS(locals)
        exec('import ' + self.moduleName, ns, ns)

    def importNames(self, *names, **kwargs):
        locals = kwargs.get('locals', False)
        ns = self._getNS(locals)
        for name in names:
            exec('from ' + self.moduleName + ' import ' + name, ns, ns)

    def _getNS(self, locals=False):
        if locals: return getCallersLocals([__name__])
        return getCallersGlobals([__name__])

def isValidName(name):
    """Return True if name is valid name in Python, False otherwise.

    @param name: name to test
    @type  name: string
    """
    class _: 
        pass
    try:
        _ = _()
        ns = dict(_=_) # <-- Not a butt!
        exec('_.%s = 1' % name, ns, ns)
    except SyntaxError: return False
    return True

def buildPackagePath(root, nodes):
    """Build a python package path nondestructively. Intermittent  __init__.py
    modules are also created along the way as needed.

    @todo: unit testing, write _build_py_tree

    @param root: absolute path of package root
    @type  root: string
    @param node: list of directory names
    @param node: list
    @rais NotImplementError: when called
    """
    raise NotImplementedError, 'buildPackagePath is not implemented'
    if not nodes: return ''
    nodes_cpy = list(nodes)
    next = nodes_cpy.pop(0)
    newroot = pj(root, next)
    if not os.path.exists(newroot):
        os.mkdir(newroot)
    initf = pj(newroot, '__init__.py')
    if not os.path.exists(initf):
        fp = open(initf, 'w'); fp.close()
    #return pj(root, _build_py_tree(newroot, next))


def argorattr(obj, *names_defaults):
    """Return mixed default values or values from attribute
    of object, if object has the attribute by the name.

    Example Usage:

    >>> class Foo:
    ...     a = 1
    ...     b = 2
    ...
    >>> f = Foo()
    >>> a, b, c = argorattr(f, ('a',-1), ('b',-2), ('c',-3))
    >>> print a, b, c
    1 2 -3

    @param names_defaults: (name, default_value) tuples
    """
    ret = ()
    for name, default in names_defaults:
        if hasattr(obj, name):
            ret += (getattr(obj, name),)
        else:
            ret += (default,)
    return ret

class CurriedCallable:
    """Example Usage:

    >>> def addThree(a, b, c=4):
    ...     return a + b + c
    ...
    >>> curried = CurriedCallable(addThree, 2, 3)
    >>> print curried()
    9
    >>> curried = CurriedCallable(addThree, 2, 3, c=5)
    >>> print curried()
    10

    Supplying an additional argument to curried:

    >>> curried = CurriedCallable(addThree, 2, 3)
    >>> print curried(c=20)
    25
    
    """

    def __init__(self, func, *pargs, **kwargs):
        self.func = func
        self.pargs = list(pargs)
        self.kwargs = dict(kwargs)
        

    def __call__(self, *pargs, **kwargs):
        kws = dict(self.kwargs)
        kws.update(dict(kwargs))
        args = self.pargs + list(pargs)
        return self.func(*args, **kws)
    
__all__ = _setAll([], locals(), 'os', 'inspect', 'implements', 'IModuleWrapper')

