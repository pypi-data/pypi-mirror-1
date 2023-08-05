import sys, re

__author__ = 'Drew Smathers'
__email__ = 'drew.smathers@gmail.com'
__version__ = '$Revision$'

def migrate(vers, namespace):
    """Call migration functions found in namepace to perform upgrade functions
    from last version >= current and up to the newest version.

    Migration function names should obey the following pattern:

    <pre>migrate[major]_[minor](_[patch])</pre>

    The version in the function name is the version we are migrating from.
    """
    p = re.compile(r'migrate(?P<current_vers>\d+_\d+(_\d+)?)')
    curr_vers_n = _vers_no(vers)
    funcs = []
    names = namespace.keys()
    for func in (f for f in names if p.match(f)):
         vers_n = _vers_no(p.match(func).groupdict()['current_vers'], '_')
         funcs.append((vers_n, func))
    funcs.sort()
    # Call migration functions in order
    for func in (f for (v,f) in funcs if v >= curr_vers_n):
        namespace[func]()

def _vers_no(vers, delim='.'):
    shift = [20, 10, 0]
    vers_n = 0
    for idx, v in enumerate(vers.split(delim)):
        vers_n |= int(v) << shift[idx]
    return vers_n

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: migrate.py [current_version]'
        sys.exit(-1)
    curvers = sys.argv[1]
    migrate(vers, globals())

