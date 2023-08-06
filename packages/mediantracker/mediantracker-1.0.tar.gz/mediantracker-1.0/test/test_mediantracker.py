#!/usr/bin/env python

# Copyright (c) 2009 John Kleint
#
# This is free software, licensed under the MIT/X11 License,
# available in the accompanying LICENSE file or via the Internet at 
# http://www.opensource.net/licenses/mit-license.html

"""
Unit tests for mediantracker.
"""


import unittest
import random

from mediantracker import MedianTracker, _ReverseCmp


class CheesyMedianTracker(object):
    """Tracks the running median of a set of values as they are added to the 
    tracker -- in a really-inefficient-but-probably-correct way.  Used for 
    testing.
    """
    
    def __init__(self, seq=[]):
        self._items = []
        for item in seq:
            self.add(item)
        
    def add(self, value):
        self._items.append(value)

    def lower_median(self):
        nitems = len(self._items)
        if nitems % 2 == 1:
            return sorted(self._items)[nitems//2]
        else:
            return sorted(self._items)[nitems//2 - 1]
            
    def upper_median(self):
        nitems = len(self._items)
        return sorted(self._items)[nitems//2]
   
   
class TestMedianTracker(unittest.TestCase):
    """Tests MedianTracker."""
    
    def insert_and_check(self, seq):
        """Compares the results of inserting seq into a MedianTracker and a 
        CheesyMedianTracker.
        """
        tracker = MedianTracker()
        cheesytracker = CheesyMedianTracker()
        for value in seq:
            tracker.add(value)
            cheesytracker.add(value)
            self.assertEqual(tracker.lower_median(), cheesytracker.lower_median())
            self.assertEqual(tracker.upper_median(), cheesytracker.upper_median())
    
    def assert_medians(self, items, lower_median, upper_median):
        """Asserts the lower median of ``items`` is ``lower_median``, 
        and the upper median is ``upper_median``.
        """
        tracker = MedianTracker()
        for item in items:
            tracker.add(item)
        self.assertEqual(tracker.lower_median(), lower_median)
        self.assertEqual(tracker.upper_median(), upper_median)
        
    def test_spot_checks(self):
        """Simple unit tests for ``MedianTracker``."""
        
        # Spot checks
        self.assert_medians([], None, None)
        self.assert_medians([1], 1, 1)
        self.assert_medians([1, 1], 1, 1)
        self.assert_medians([1, 2], 1, 2)
        self.assert_medians([2, 1], 1, 2)
        self.assert_medians([0, 0, 0], 0, 0)
        
        self.assert_medians([1, 2, 3], 2, 2)
        self.assert_medians([1, 3, 2], 2, 2)
        self.assert_medians([2, 1, 3], 2, 2)
        self.assert_medians([2, 3, 1], 2, 2)
        self.assert_medians([3, 1, 2], 2, 2)
        self.assert_medians([3, 2, 1], 2, 2)
        
        self.assert_medians([1, 2, 2], 2, 2)
        self.assert_medians([1, 2, 2], 2, 2)
        self.assert_medians([2, 1, 2], 2, 2)
        self.assert_medians([2, 2, 1], 2, 2)
        self.assert_medians([2, 1, 2], 2, 2)
        self.assert_medians([2, 2, 1], 2, 2)
        
        self.assert_medians([1, 2, 3, 4], 2, 3)
        self.assert_medians([4, 3, 2, 1], 2, 3)
        self.assert_medians([1, 1, 2, 2], 1, 2)
        self.assert_medians([2, 2, 1, 1], 1, 2)
        self.assert_medians([1, 1, 1, 2], 1, 1)
        self.assert_medians([2, 1, 1, 1], 1, 1)
        self.assert_medians([1, 2, 2, 2], 2, 2)
        self.assert_medians([2, 2, 2, 1], 2, 2)
        
        self.assert_medians([1, 2, 3, 4, 5], 3, 3)
        self.assert_medians([5, 4, 3, 2, 1], 3, 3)
        self.assert_medians([1, 2, 3, 4, 4], 3, 3)
        self.assert_medians([1, 2, 2, 3, 3], 2, 2)
        self.assert_medians([1, 2, 2, 2, 3], 2, 2)
        self.assert_medians([-1, -2, -3, -4, -5], -3, -3)
        self.assert_medians([-5, -4, -3, -2, -1], -3, -3)

    def test_random_lists(self):
        """Tests with random lists of increasing size."""
        # Uncomment this if you like to roll deterministically
        # random.seed(1)  
        num_iters = 100

        for numvals in xrange(1, num_iters):
            # Check sorted ascending and descending
            self.insert_and_check(xrange(numvals))
            self.insert_and_check(reversed(xrange(numvals)))
            # Check random permutations of 0..n-1
            items = range(numvals)
            random.shuffle(items)
            self.insert_and_check(items)
            random.shuffle(items)
            self.insert_and_check(items)
            random.shuffle(items)
            self.insert_and_check(items)
            # Check a list with many repeats
            items = [random.randint(0, numvals//5) for i in xrange(numvals)]
            self.insert_and_check(items)
            # Check a sparse float list
            items = [random.random() for i in xrange(numvals)]
            self.insert_and_check(items)
            
            # Check __init__ and __iter__
            tracker = MedianTracker(items)
            self.assertEqual(list(sorted(tracker)), list(sorted(items)))
            # Check __len__
            self.assertEqual(len(tracker), len(items))
        

class TestReverseCmp(unittest.TestCase):
    """Unit test for ``_ReverseCmp``."""

    def test_reversecmp(self):
        """Unit tests for ``_ReverseCmp``."""
        one = _ReverseCmp(1)
        two = _ReverseCmp(2)
        
        self.assert_(not (one < two))
        self.assert_(not (one <= two))
        self.assert_(one > two)
        self.assert_(one >= two)
        self.assert_(not (one == two))
        self.assert_(one != two)
    
        self.assert_(not (one < 2))
        self.assert_(not (one <= 2))
        self.assert_(one > 2)
        self.assert_(one >= 2)
        self.assert_(not (one == 2))
        self.assert_(one != 2)
        
        self.assert_(not (1 < two))
        self.assert_(not (1 <= two))
        self.assert_(1 > two)
        self.assert_(1 >= two)
        self.assert_(not (1 == two))
        self.assert_(1 != two)
    
        items = [_ReverseCmp(item) for item in [1, 2, 3]]
        items.sort()
        sorteditems = [item.get() for item in items]
        self.assertEqual(sorteditems, [3, 2, 1])
        
        items = [_ReverseCmp(item) for item in [3, 2, 1]]
        items.sort()
        sorteditems = [item.get() for item in items]
        self.assertEqual(sorteditems, [3, 2, 1])
        
        items = [_ReverseCmp(item) for item in [3, 2, 1]]
        sorteditems = [item.get() for item in sorted(items, reverse=True)]
        self.assertEqual(sorteditems, [1, 2, 3])
    
    
# Running as a script executes unit tests
if __name__ == "__main__":
    unittest.main()
    
