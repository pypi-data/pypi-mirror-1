"""Differences for sequences of objects

$Id$
"""

__author__ = 'Drew Smathers'
__copyright__ = 'Copyright 2005, Drew Smathers'
__version__ = '$Revision$'[11:-2]

from xix.utils.interfaces import IDiff, IDiffFactory
from xix.utils.comp.interface import implements


class AbstractDiff:
    """A diff represents differences between a source and target list of objects.
    It is up to the application using this library to compute the diff object - 
    or object that adapts this interface

    same: list of objects that are same between the source and target lists
    missing: list of objects that are in source list but not in target list
    added: list of objects that are in target list but not in source list
    """

    implements(IDiff)

    def __init__(self, same, missing, added):
        self.same = same
        self.missing = missing
        self.added = added


class SequentialDiffFactory:
    """Generates Diffs between source and target objects, considering sequence
    of appearance.
    """
    
    implements(IDiffFactory)

    def diff(self, source, target):
        """Example:

        # >>> l1 = [1,2,3,4,5]
        # >>> l2 = [3,4,5,1,2]
        # >>> diffFactory = SequentialDiffFactory()
        # >>> d = diffFactory.diff(source, target)
        # >>> d.same
        # [3, 4, 5]
        # >>> d.missing
        # [1, 2]
        # >>> d.added
        # [1, 2]
        """
        raise NotImplementedError, 'diff has not been implemented yet'
        
        

class NonSequentialDiffFactory:
    """Generates Diffs between source and target objects, without consideration
    to sequence of appearces of objects.
    """

    implements(IDiffFactory)

    def diff(self, source, target):
        """Example usage:

        >>> l1 = [1, 2, 3, 4, 5]
        >>> l2 = [3, 4, 7, 1, 8, 9]
        >>> diffFactory = NonSequentialDiffFactory()
        >>> d = diffFactory.diff(l1, l2)
        >>> d.same
        (1, 3, 4)
        >>> d.missing
        (2, 5)
        >>> d.added
        (7, 8, 9)
        """
        added = tuple([elm for elm in target if elm not in source])
        missing = tuple([elm for elm in source if elm not in target])
        same = tuple([elm for elm in source if elm in target])
        return AbstractDiff(same, missing, added)

class DictionaryDiffFactory:
    """Return diff of two dictionaries.  Entries in same, added and missing
    lists are key, value pairs. (k,v)
    """

    implements(IDiffFactory)

    keyValueDiffFactory = NonSequentialDiffFactory()

    def diff(self, source, target):
        """Example Usage:

        >>> d1 = {'a':1, 'b':2, 'c':3}
        >>> d2 = {'b':4, 'c':3, 'a':2}
        >>> diffFactory = DictionaryDiffFactory()
        >>> d = diffFactory.diff(d1, d2)
        >>> len(d.same)
        1
        >>> len(d.missing)
        2
        >>> len(d.added)
        2
        >>> d.same
        (('c', 3),)
        >>> [int(elm in d.missing) for elm in (('a',1), ('b',2))]
        [1, 1]
        >>> [int(elm in d.added) for elm in (('a',2), ('b',4))]
        [1, 1]
        """
        return self.keyValueDiffFactory.diff(source.items(), target.items())


class PrettyDiff:
    """A pair of sequences alligned representing a Diff.  The first sequence
    represents the source of the diff, the secound the target.  None entries
    in first sequence are row-alligned with corresponding items from added
    tuple.  None entries in seconds sequence are row-alligned with corresponding
    items form missing tuple.  All other entries correspong to same list


    Example Usage:

    >>> src = set([1,4,6,7,8])
    >>> tgt = set([0,1,6,9,10])
    >>> added = tuple(tgt - src)
    >>> missing = tuple(src - tgt)
    >>> same = tuple(src.intersection(tgt))
    >>> diff = AbstractDiff(same, missing, added)
    >>> pretty_diff = PrettyDiff(diff)
    >>> print pretty_diff
    ((1, 1), (6, 6), (8, None), (4, None), (7, None), (None, 0), (None, 9), (None, 10))

    Iterating over rows:

    >>> for row in pretty_diff:
    ...   print row
    ...
    (1, 1)
    (6, 6)
    (8, None)
    (4, None)
    (7, None)
    (None, 0)
    (None, 9)
    (None, 10)
    
    """

    def __init__(self, diff):
        added = tuple([(None, add) for add in diff.added])
        missing = tuple([(miss, None) for miss in diff.missing])
        same = tuple([(sam, sam) for sam in diff.same])
        self.diff = same + missing + added

    def sort(self, cmpfunc=None):
        """Sort this pretty diff using optional compare function or default
        comparison of objects.

        Example Usage:

        >>> src = set([1,4,6,7,8])
        >>> tgt = set([0,1,6,9,10])
        >>> added = tuple(tgt - src)
        >>> missing = tuple(src - tgt)
        >>> same = tuple(src.intersection(tgt))
        >>> diff = AbstractDiff(same, missing, added)
        >>> pretty_diff = PrettyDiff(diff)
        >>> pretty_diff.sort()
        >>> print pretty_diff
        ((None, 0), (1, 1), (4, None), (6, 6), (7, None), (8, None), (None, 9), (None, 10))
        
        """
        compare = cmpfunc
        if compare is None:
            def compare(obj1, obj2):
                return cmp(obj1, obj2)
        class Proxy(object):
            def __init__(self, obj, compfunc):
                self.obj = obj
                self.compfunc = compfunc
            def __cmp__(self, other):
                return self.compfunc(self.obj, other.obj)
        ref = [(Proxy(row[int(row[0] is None)], compare), row[0], row[1]) \
              for row in self]
        ref.sort()
        self.diff = tuple([(row[1],row[2]) for row in ref])

    def __str__(self):
        return str(self.diff)

    def __iter__(self):
        def iterrows(inst):
            for row in inst.diff:
                yield row
        return iterrows(self)
        
        
