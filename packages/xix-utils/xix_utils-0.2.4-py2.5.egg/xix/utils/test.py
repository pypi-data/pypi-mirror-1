## Test utilities

from glob import glob
try:
    from zope.testing import doctest
except:
    import doctest
import os
from UserDict import UserDict

__author__ = 'Drew Smathers'
__contact__ = 'drew smathers at gmail dot com'
__version__ = '$Revision$'

class DocFileSuiteBuilder:
    """Covenience utility class for building test suites for documentation files.

    If a module is given with mod argument, then setUp and tearDown functions for
    each test can be derived based on naming convention:

       Example_docttest.txt (filename)
       Example_docttest_setUp (setUp function name in mod)
       Example_docttest_tearDown (tearDown function name in mod)
       Example_docttest_globs (dictionary of globals in mod)
    
    Note. test directories are not relative to module, but relative to location
    of script executing unit tests - that is module_relative flag is set to false
    for each DocTestSuite instance.
    """

    def __init__(self, mod=None, directories=[], extensions=('.txt', '.html'), recursive=True):
        self.mod = mod
        self.directories = [os.path.abspath(d) for d in directories]
        self.extensions = extensions
        self.suites = self._buildSuites(recursive)

    def _buildSuites(self, recursive):
        files = []
        suites = []
        for directory in self.directories:
            def addfiles(d):
                for ext in self.extensions:
                    files.extend(glob(d + '/*' + ext))
            if recursive:
                for root, dirs, filenames in os.walk(directory):
                    addfiles(root)
            else:
                addfiles(directory)
        files.sort()
        for docfile in files:
            kwargs = {}
            if self.mod:
                name = '.'.join((os.path.split(docfile)[1]).split('.')[:-1])
                for bad in ('-', '.'):
                    name = name.replace(bad, '_')
                func = lambda test : None
                globs = {}
                for arg, default in (('setUp', func), ('tearDown', func), ('globs', globs)):
                    kwargs[arg] = getattr(self.mod, name + '_' + arg, default)
            suite = doctest.DocFileSuite(docfile, module_relative=False, **kwargs)
            suites.append(suite)
        return suites

    def addToSuite(self, suite):
        for test in self.suites:
            suite.addTest(test)

        
