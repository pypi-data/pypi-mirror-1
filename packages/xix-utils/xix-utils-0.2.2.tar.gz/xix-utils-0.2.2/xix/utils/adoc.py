"""agile documentation (doctest) utilities
"""

from xix.utils.comp.interface import implements
from xix.utils.interfaces import IDocTestElement, IDocTestUnit
from xix.utils.interfaces import IDocTestLineup, IInterpreterSession

__author__ = 'Drew Smathers'
__contact__ = 'drew.smathers@gmail.com'
__license__ = 'MIT'
__revision__ = '$Revision$'



class DocTestElement:
    """DocTestElement provides the IDocTestElement

    >>> IDocTestElement.providedBy(DocTestElement)
    """
    implements(IDocTestElement)

class InterpreterLine(DocTestElement):
    pass

class InterpreterInput(InterpreterLine):
    def __init__(self, input):
        self.input = input

class InterpreterOutput(InterpreterLine):
    def __init__(self, output):
        self.output = output

class DocTestUnit:
    implements(IDocTestUnit) 
    lines = []

class DocTestLineup(DocTestUnit):
    pass
    
class InterpreterLineup(DocTestLineup):
    implements(IInterpreterSession)

    interpreter = None


class PydocElement(DocTestElement):
    pass

class PydocMetatag(PydocElement):

    def __init__(self, tag, name=None, desc=None):
        self.tag = tag
        self.name = name or ''
        self.desc = desc or ''

####################################
# 
