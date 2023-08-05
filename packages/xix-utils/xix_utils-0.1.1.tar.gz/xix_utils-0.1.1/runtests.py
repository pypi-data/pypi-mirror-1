#!/usr/bin/env python

###############################################################################
#
# $Id: runtests.py 177 2005-12-20 19:59:38Z drew $
#
###############################################################################

import unittest
import doctest
import os, inspect
from glob import glob
from utiltests import util_doctests
from tests import doctests
from xix.utils.config import configFactory

__author__ = 'Drew Smathers'
__copyright__ = 'Copyright (c) 2005 Drew Smathers'
__license__ = 'MIT'
__version__ = '$Revision: 177 $'[11:-2]

configFactory.addResource('xix-unittests.cfg', 'unittests.cfg')

docfiles = glob('tests/doctests/txt/*.txt')
docfiles.sort()
        
def main():
    suite = unittest.TestSuite() 
    for source in util_doctests:
        suite.addTest(doctest.DocTestSuite(source))
    for docfile in docfiles:
        suite.addTest(doctest.DocFileSuite(docfile))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    main()
    
