'''
rules rules!

TODO create a badass rules engine

$Id: rules.py 159 2005-12-02 20:35:19Z drew $
'''

from xix.utils.interfaces import IRule, IRuleChain
from xix.utils.python import allexcept
from xix.utils.config import configFactory
from xix.utils.comp.interface import implements

__author__    = 'Drew Smathers <drew.smathers@gmail.com>'
__version__   = '$Revision: 159 $'[11:-2]
__copyright__ = 'Copyright (C) 2005, Drew Smathers'


_rulescfg = configFactory.getConfig()
    
# Our engine registry
engineRegistry = _rulescfg.engineRegistry


class RulesException(Exception):
    '''Generic RulesException.
    '''
    pass

class RulesEngineAlreadyRegisteredException(RulesException):
    '''Raised when when trying to register a rules engine with registered name.
    '''
    pass

class Rule:
    '''Validation rule functor.
    '''
    implements(IRule)
    
    def __call__(self, *pargs, **kwargs):
        '''Example:

        >>> rule  = Rule()
        >>> rule("the world")
        True
        '''
        return True

class RuleChain:
    '''Functor for series of short-circuiting rules.
    '''
    implements(IRuleChain)

    def __init__(self, rules=None):
        self.rules = rules or []

    def __call__(self, *pargs, **kwargs):
        '''Example:

        >>> class MyRule(Rule):
        ...     def __call__(self, *pargs, **kwargs):
        ...         return False
        ...
        >>> rule1, rule2 = Rule(), MyRule()
        >>> chain = RuleChain([rule1, rule2])
        >>> chain("me up an beat me with a shoe")
        False
        '''
        result = True
        for rule in self.rules:
            result &= rule(*pargs, **kwargs)
            if not result: break # short-circuit
        return result

def registerEngine(engineName, rulesEngine):
    '''Register a rules enging with name engineName.
    '''
    if engineName in engineRegistry:
        raise RulesEngineAlreadyRegisteredException, \
            'Engine with name %s already registered' % engineName
    engineRegistry[engineName] = rulesEngine


__all__ = allexcept('IRule', 'IRuleChain', 'allexcept', 'configFactory', 'implements')    
