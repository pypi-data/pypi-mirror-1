#!/usr/bin/env python

import unittest
from compset import CompSet


class CompSetFactory(object):
    """This is just a simple factory for repeatedly creating sets from a
    simple given universe."""
    
    def __init__(self, numElements=0):
        """numElements is the number of elements in the universe.
        The universe will contain the numbers [0..numElements)."""
        self.numElements = numElements

    def new(self, initialContents=[]):
        """Create a new CompSet with our universe."""
        return CompSet(initialContents, universalSetSize=self.numElements,
                       universeIterator=xrange(self.numElements))
        

class CompSetTest(unittest.TestCase):
    def setUp(self):
        self.factory = CompSetFactory()
        
    def testEmptySet(self):
        a = self.factory.new()
        self.assertEqual(len(a), 0)

    def testContains(self):
        a = self.factory.new([3, 4, 5, 6])
        self.assertEqual(3 in a, True)
        self.assertEqual(4 in a, True)
        self.assertEqual(5 in a, True)
        self.assertEqual(6 in a, True)
        self.assertEqual(7 in a, False)

    def testComplementAdd(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        a.complement()
        self.assertEqual(3 in a, False)
        self.assertEqual(7 in a, True)

    def testUniverse(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        a.complement()
        self.assertEqual([0, 1, 2, 7, 8, 9], list(a))

    def testUnion(self):
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        c = a.union(b)
        self.assertEqual(list(c), range(1, 7))

    def testInvertUnion1(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        b.complement()
        c = a.union(b)
        self.assertEqual(list(c), [0, 3, 4, 5, 6, 7, 8, 9])

    def testInvertUnion2(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        a.complement()
        c = a.union(b)
        self.assertEqual(list(c), [0, 1, 2, 3, 4, 7, 8, 9])

    def testInvertInvertUnion(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        a.complement()
        b.complement()
        c = a.union(b)
        self.assertEqual(list(c), [0, 1, 2, 5, 6, 7, 8, 9])

    def testIntersection(self):
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        c = a.intersection(b)
        self.assertEqual(list(c), [3, 4])

    def testInvertIntersection1(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        a.complement()
        c = a.intersection(b)
        self.assertEqual(list(c), [1, 2])

    def testInvertIntersection2(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        b.complement()
        c = a.intersection(b)
        self.assertEqual(list(c), [5, 6])

    def testInvertInvertIntersection(self):
        self.factory = CompSetFactory(10)
        a = self.factory.new([3, 4, 5, 6])
        b = self.factory.new([1, 2, 3, 4])
        a.complement()
        b.complement()
        c = a.intersection(b)
        self.assertEqual(list(c), [0, 7, 8, 9])


if __name__ == '__main__':
    unittest.main()
