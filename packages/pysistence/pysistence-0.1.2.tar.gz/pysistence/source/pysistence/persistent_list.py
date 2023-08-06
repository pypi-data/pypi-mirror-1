"""
This module contains the PList class.
"""
try:
    from itertools import izip_longest
except ImportError:
    from itertools import izip, chain, repeat
    def izip_longest(*args, **kwds):
        # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
        fillvalue = kwds.get('fillvalue')
        def sentinel(counter = ([fillvalue]*(len(args)-1)).pop):
            yield counter()         # yields the fillvalue, or raises IndexError
        fillers = repeat(fillvalue)
        iters = [chain(it, sentinel(), fillers) for it in args]
        try:
            for tup in izip(*iters):
                yield tup
        except IndexError:
            pass


from pysistence.util import reverse_tuple

def mkList(*items):
    """
    Make a new persistent list from *items*.
    """
    reversed_items = reverse_tuple(items)
    new_list = EmptyList()
    for item in reversed_items:
        new_list = new_list.cons(item)

    return new_list

class PList(object):
    """
    A PList is a list that is mutated by copying.  This makes them effectively
    immutable like tuples.  The difference is that tuples require you to copy
    the entire structure.  PLists will reuse as much of your existing list as
    possible.
    """
    __slots__ = ['_first', '_rest']
    def __init__(self, first, rest=None):
        self._first = first
        self._rest = rest

    @property
    def first(self):
        """
        Get the first item in this list.
        """
        return self._first
    
    @property
    def rest(self):
        """
        Get all items except the first in this list.
        """
        return self._rest

    @property
    def frest(self):
        """
        The first item of the rest.  Equivalent to some_list.rest.first
        """
        return self.rest.first

    def cons(self, next_item):
        """
        Create a new list with *next_item* in front.
        """
        return PList(next_item, self)

    def without(self, *items):
        """
        Return a new PList with *items* removed
        """
        removeset = set(items)
        return mkList(*(elem for elem in self if elem not in removeset))
        

    def __iter__(self):
        current = self
        while current:
            yield current._first
            current = current._rest
    
    def __repr__(self):
        """Note that this can be computationally expensive, O(n)"""
        str_value = str(list(iter(self)))
        return 'PList(%s)' % str_value

    def __eq__(self, other):
        if not hasattr(other, '__iter__'):
            return False

        # We can assume that we're not empty since this isn't an empty list
        if not other:
            return False

        zipped_iter = izip_longest(self, other)
        cmp_iterator = (item1 == item2 for (item1, item2) in zipped_iter)
        return all(cmp_iterator)

    def __nonzero__(self):
        return True
            

class EmptyList(object):
    def cons(self, next_item):
        return PList(next_item, None)

    def __iter__(self):
        return iter(())

    def __nonzero__(self):
        return False
