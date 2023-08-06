# Copyright (c) 2009 Jason M Baker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
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
from pysistence.exceptions import ItemNotFoundError

def make_list(*items):
    """
    Make a new persistent list from *items*.
    """
    reversed_items = reverse_tuple(items)
    new_list = EmptyList()
    for item in reversed_items:
        new_list = new_list.cons(item)

    return new_list

# stub for backwards compatibility
mkList = make_list

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
        return make_list(*(elem for elem in self if elem not in removeset))

    def concat(self, next_list):
        """
        Concatenate this list with another list.
        """
        reversed_self = reversed(self)
        new_list = next_list
        for item in reversed_self:
            new_list = new_list.cons(item)
        return new_list

    def replace(self, old, new):
        """
        Return a new list that has new instead of old.  Will raise
        an exception if old is not found.
        """
        seen_items = EmptyList()
        for item in self._plist_iter():
            if item.first == old:
                base_list = item.rest
                if base_list:
                    new_list = base_list.cons(new)
                else:
                    new_list = make_list(new)
                for seen_item in seen_items:
                    new_list = new_list.cons(seen_item.first)
                return new_list
            else:
                seen_items = seen_items.cons(item)
        else:
            msg = 'Item %s not found in list' % old
            raise ItemNotFoundError, msg

    def reverse(self):
        """
        Make a new PList that is the reverse of this one.
        """
        new_list = EmptyList()
        for item in self:
            new_list = new_list.cons(item)
        return new_list

    def _plist_iter(self):
        head = self
        while head:
            yield head
            head = head.rest
            
    def __reversed__(self):
        return iter(self.reverse())

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

    __add__ = concat
            

class EmptyList(object):
    def cons(self, next_item):
        return PList(next_item, None)

    def __iter__(self):
        return iter(())

    def __nonzero__(self):
        return False
