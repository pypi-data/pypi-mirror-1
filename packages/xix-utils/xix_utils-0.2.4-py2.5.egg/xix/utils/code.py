"""code ...
"""

from xix.utils.comp.interface import implements
from xux.utils.interfaces import ICodeRunner

import warnings

import commands

__author__ = 'Drew Smathers'
__revision__ = '$Revision$'
__contact__ = 'drew.smathers@gmail.com'
__license__ = 'MIT'

warnings.warn('xix.utils.code module is pre-alpha/unstable')

class CodeRunner(ICodeRunner):
    implements(ICodeRunner)
    
    def run(self, code):
        pass

class CommandRunner(CodeRunner):

    def run(self, command):
        return commands.getstatusoutput(command)


