'''
I contain some swell functions inspecting modules, classes
and functions in a package.

-=- BEGIN LICENSE -=-

Copyright (c) 2005 Drew Smathers

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.

-=- END LICENSE -=-

'''

# $Id: source.py 159 2005-12-02 20:35:19Z drew $

# Move loadObject, getCaller into more apropriately named module

import sys, inspect, imp

__revision__ = '$Id: source.py 159 2005-12-02 20:35:19Z drew $'

__author__ = 'Drew Smathers <drew.smathers@gmail.com>'
__version__ = '$Revision: 159 $'[11:-2]
__copyright__ = 'Copyright (C) 2005, Drew Smathers'

def getsource(obj):
    '''I get you the raw source code for an object.
    @param obj: object itself or string representation (eg. xix.rend.template)
    '''
    return _getsrc(obj, inspect.getsource)

def getsourcelines(obj):
    '''@see getsource
    '''
    return _getsrc(obj, inspect.getsourcelines)

def getdoc(obj):
    '''@see getsource
    '''
    return _getsrc(obj, inspect.getdoc)

def getcomments(obj):
    '''@see getsource
    '''
    return _getsrc(obj, inspect.getcomments)

def stripdoc(source):
    '''I strip doc out of source string. This function has not beem
    implemented yet.
    @param source: source string
    @type  source: str
    @raises: NotImplementedError
    @todo: implement and test
    '''
    raise NotImplementedError

def stripcomments(source):
    '''I strip comments out of a source string. This function has
    not been implemented yet.
    @param source: source string
    @type  source: str
    @raises: NotImplementedError
    @todo: implement and test
    '''
    raise NotImplementedError

def getCallersGlobals( internal_ns ):
    '''
    Get globals of caller.

    @param internal_ns: names to ignore in stack search
    '''
    intns = list(internal_ns)
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
        globals = callers_frame.f_globals
        return globals
    finally: 
        del callers_frame

# And our wonderful voodoo ;)
def loadObject( moduleString, fakepath=None ):
    '''Given a module string such as: xix.utils.source,
    load the module or object as and return the loaded entity.

    @param moduleString: module string such as 'xix.utils.source'
    @type  moduleString: str
    '''
    mods = moduleString.split('.')
    mbr = mods[len(mods)-1]
    path = fakepath or sys.path
    loaded = None
    fp = None
    for mod, idx in zip(mods, range(len(mods))):
        if mod == mbr and mod in dir( loaded ):
            return getattr( loaded, mod )
        try:
            fp, pathname, descr = imp.find_module( mod, path )
        except:
            if fp: fp.close()
            return _load_from_hierarch( mods[idx:], loaded )
        try: 
            loaded = imp.load_module(moduleString, fp, pathname, descr)
            path = loaded.__path__
        finally:
            if fp: fp.close()
    return loaded

####################################
# End lib functions ... begin voodoo


def _load_from_hierarch ( hierarch, loaded ):
    for obj in hierarch:
        loaded = getattr(loaded, obj)
    return loaded

def _getsrc(obj, func):
    if type(obj) == str:
        loaded = loadObject(obj)
        return func(loaded)
    else:
        return func(obj)

__all__ = [ 'getsource', 'getsourcelines', 'getdoc', 'getcomments', 'stripdoc', 'stripcomments' ]


