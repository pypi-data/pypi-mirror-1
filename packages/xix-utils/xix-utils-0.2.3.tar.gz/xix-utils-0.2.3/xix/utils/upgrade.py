import sys, re

__author__ = 'Drew Smathers'
__email__ = 'drew.smathers@gmail.com'
__version__ = '$Revision$'

def _upgrade(vers, namespace, func_pfx='upgrade', sort_func=None, select_func=None):
    p = re.compile(r'%s(?P<current_vers>\d+_\d+(_\d+)?)' % func_pfx)
    curr_vers_n = _vers_no(vers)
    funcs = []
    ns = namespace
    if not isinstance(ns, dict):
        ns = ns.__dict__
    names = ns.keys()
    for func in (f for f in names if p.match(f)):
         vers_n = _vers_no(p.match(func).groupdict()['current_vers'], '_')
         funcs.append((vers_n, func))
    #funcs.sort()
    sort_func(funcs)
    # Call migration functions in order
    for func in (f for (v,f) in funcs if select_func(curr_vers_n, v)):
        ns[func]()

def upgrade(vers, namespace, func_pfx='upgrade'):
    """Call upgrade functions found in namepace to perform upgrade functions
    from last version >= current and up to the newest version.

    Upgrade function names must obey the following pattern:

    <pre>upgrade[major]_[minor](_[patch])</pre>

    The version in the function name is the version we are upgrading from.
    So if you are upgrading from a version 0.1.3 to 0.2.1 for example, all functions
    >= 0.1.3 will be executed and in order.
    """
    _upgrade(vers, namespace, func_pfx=func_pfx,
            sort_func=(lambda l: l.sort()),
            select_func=(lambda cv, v: v >= cv))

def downgrade(vers, namespace, func_pfx='downgrade'):
    """Like upgrade except we apply "downgrade" functions in reverse order
    down to and including the version we want to downgrade to.
    """
    def sorter(l):
        l.sort()
        l.reverse()
    _upgrade(vers, namespace, func_pfx=func_pfx,
            sort_func=sorter,
            select_func=(lambda cv, v: v >= cv))

# backwards comp
def migrate(vers, namespace):
    import warnings
    warnings.warn('Function migrate has been deprecated. use xix.utils.upgrade.upgrade instead.')
    return upgrade(vers, namespace, 'migrate')

def _vers_no(vers, delim='.'):
    shift = [20, 10, 0]
    vers_n = 0
    for idx, v in enumerate(vers.split(delim)):
        vers_n |= int(v) << shift[idx]
    return vers_n

