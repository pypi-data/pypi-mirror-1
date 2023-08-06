#!/usr/bin/env python

# Copyright (c) 2009 John Kleint
#
# This is free software, licensed under the MIT/X11 License,
# available in the accompanying LICENSE file or via the Internet at 
# http://www.opensource.net/licenses/mit-license.html


"""
Track the median of a stream of values "on-line" in reasonably efficient 
fashion.

Usage::

    from mediantracker import MedianTracker
    tracker = MedianTracker()
    tracker.add(1)
    tracker.add(2)
    tracker.add(3)
    tracker.add(4)
    assert tracker.lower_median() == 2
    assert tracker.upper_median() == 3
    
``MedianTracker`` supports efficient median queries on and dynamic
additions to a list of values. It provides both the lower and upper median
of all values seen so far. Any ``__cmp__()``-able object can be tracked,
in addition to numeric types. ``add()`` takes *log(n)* time for a tracker
with *n* items; ``lower_median()`` and ``upper_median()`` run in constant
time. Since all values must be stored, memory usage is proportional to the
number of values added (*O(n)*).

The values can be accessed via iteration over the ``MedianTracker``,
though they are not ordered in any particular way::

    sum = 0.0
    for val in tracker:
        sum += val
    mean = sum / len(tracker) 

Use this module if you are processing values "on-line," one at a time, as
they arrive, and need to know the new median after each new value (or
batch of values). If you just want the median of a whole list, there are
much more efficient linear-time median (or more general k-th smallest
selection) algorithms. Using this module will take *O(nlogn)* time and an
extra *O(n)* space to compute the median of *n* items. On the other hand,
a ``MedianTracker`` will only take *O(nlogn + m)* time for any sequence of
*n* adds and *m* median queries, whereas running a traditional
non-incremental median algorithm *m* times would take *O(n*m)*.

Finally, some sources define the median of an even-length list to be the
average of the middle two values. This is easily and efficiently computed
(in constant time)::

    tracker = MedianTracker([1, 2, 3, 4])
    median = (tracker.lower_median() + tracker.upper_median()) / 2.0
    assert median == 2.5


"""


from heapq import heappush, heappop


__all__ = ['MedianTracker']


class _ReverseCmp(object):
    """
    Reverses the sense of ``__cmp__()`` for the contained object::
    
    >>> one = _ReverseCmp(1)
    >>> one < 2
    False
    >>> one > 2
    True
    
    """
    
    __slots__ = ['_obj']         # Save some memory
    
    def __init__(self, obj):
        self._obj = obj
    
    def __cmp__(self, other):
        if isinstance(other, _ReverseCmp):
            # Calling "self._obj < other" would result in a double-reverse
            # if other is also a _ReverseCmp, so we have to check.
            if self._obj < other.get():
                return 1
            elif self._obj > other.get():
                return -1
            else:
                return 0
        else:
            if self._obj < other:
                return 1
            elif self._obj > other:
                return -1
            else:
                return 0

    def get(self):
        """Returns the object stored in this ``_ReverseCmp``."""
        return self._obj
        
    def __unicode__(self):
        return unicode(self._obj)
        
    def __str__(self):
        return str(self._obj)
        

class MedianTracker(object):
    """
    Track the ``lower_median()`` and ``upper_median()`` of all values 
    ``add()``ed so far::
    
        tracker = MedianTracker()
        tracker.add(1)
        tracker.add(2)
        tracker.add(3)
        tracker.add(4)
        assert tracker.lower_median() == 2
        assert tracker.upper_median() == 3
    
    Any on-line exact median algorithm must store all of the values, so
    memory usage is proportional to the number of values added. ``add()``
    takes log(n) time for a tracker with n items; ``lower_median()`` and
    ``upper_median()`` run in constant time. Supports iteration over the
    list of values, though not in any particular order.
    
    Any object which implements ``__cmp__`` can be tracked, in addition to
    numeric types.
    
    """
    
    # Basic idea: keep a max-heap of the smaller half of items and a
    # min-heap of the larger half. Rebalance as necessary when adding
    # values. With an odd number of items (one heap bigger than the
    # other), both the upper and lower median are the highest-priority
    # item in the larger of the two heaps. With an even number of items,
    # the lower median is the highest-priority (largest) value in the
    # lower half; the upper median is the highest-priority (smallest)
    # value in the upper half.
    
    def __init__(self, seq=[]):
        """Initializes a new empty ``MedianTracker``.  
        You can optionally provide a sequence ``seq`` of initial values.
        """ 
        self._lower = []         # Items <= median; a max-heap 
        self._upper = []         # Items >= median; a min-heap
        for value in seq:
            self.add(value)
            
    def add(self, value):
        """Adds a ``value`` to the tracker."""
        # Since python's heapq only provides a min-heap, and we need a
        # max-heap for the lower half of the values, we wrap values in the
        # lower half with _ReverseCmp to reverse the sense of comparisons.

        # Push onto the appropriate heap
        lowermedian = self.lower_median()
        if (value <= lowermedian):
            # _ReverseCmp reverses the sense of comparisons used by 
            # heapq's heap-ordering calculations, providing a max-heap
            heappush(self._lower, _ReverseCmp(value))      
        else:
            heappush(self._upper, value)
            
        # Rebalance heaps if necessary
        numlower = len(self._lower)
        numupper = len(self._upper)
        assert abs(numlower - numupper) <= 2
        
        # Lower is too big: put largest item into upper
        if numlower > numupper + 1:
            heappush(self._upper, heappop(self._lower).get())
        # Upper is too big: put smallest item into lower
        elif numupper > numlower + 1:
            heappush(self._lower, _ReverseCmp(heappop(self._upper)))
        assert abs(len(self._lower) - len(self._upper)) <= 1
            
        
    def lower_median(self):
        """Returns the lower median of the values tracked.  
        Returns ``None`` if the tracker is empty.
        """
        numlower = len(self._lower)
        numupper = len(self._upper)
        assert abs(numlower - numupper) <= 1
        
        if numlower == 0 and numupper == 0:
            return None
        if numlower >= numupper:
            return self._lower[0].get()
        else:
            return self._upper[0]
            
            
    def upper_median(self):
        """Returns the upper median of the values tracked.  
        Returns ``None`` if the tracker is empty.
        Note the upper and lower medians will be equal for an odd number 
        of values.
        """
        numlower = len(self._lower)
        numupper = len(self._upper)
        assert abs(numlower - numupper) <= 1
        
        if numlower == 0 and numupper == 0:
            return None
        if numupper >= numlower:
            return self._upper[0]
        else:
            return self._lower[0].get()
            
            
    def __len__(self):
        """Returns the number of values added to this ``MedianTracker`` so far.
        """
        return len(self._lower) + len(self._upper)
            
            
    def __iter__(self):
        """Iterator over the values stored in this ``MedianTracker``.
        The order of values may be different than the order in which they were 
        added.
        """
        for val in self._lower:
            yield val.get()
        for val in self._upper:
            yield val
        
    
# Running as a script executes unit tests
if __name__ == "__main__":
    import sys, unittest
    sys.path.append('test')

    SUITE = unittest.defaultTestLoader.loadTestsFromName('test_mediantracker')
    unittest.TextTestRunner(verbosity=2).run(SUITE)

