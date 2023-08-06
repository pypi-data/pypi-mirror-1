"""Note that the various set operations implemented here do in some cases
modify their arguments. This is because these methods were written with
speed in mind, not generality. In many cases it is simpler to modify an
existing set than it is to build a new one that's a copy of an old and then
modify that."""


class InfiniteSetError(Exception): pass


class CompSet(object):
    def __init__(self, initialContents=[], invert=False,
                 universalSetSize=None, universeIterator=None):
        self.set = set(initialContents)
        self._invert = invert
        self.universalSetSize = universalSetSize
        self.universeIterator = universeIterator

    def complement(self):
        self._invert = not self._invert
    
    def __contains__(self, e):
        if self._invert:
            return not self.set.__contains__(e)
        else:
            return self.set.__contains__(e)

    def __len__(self):
        if self._invert:
            if self.universalSetSize is None:
                raise InfiniteSetError()
            return self.universalSetSize - len(self.set)
        else:
            return len(self.set)

    def add(self, e):
        if self._invert:
            self.set.discard(e)
        else:
            self.set.add(e)
                
    def update(self, elements):
        '''Add everything in elements to the set.'''
        # Do what self.add would do, but without calling self.add repeatedly.
        if self._invert:
            f = self.set.discard
        else:
            f = self.set.add
        # Don't use map here, as we may be passed some kind of iterator or
        # generator.
        for e in elements:
            f(e)
                
    def discard(self, e):
        if self._invert:
            self.set.add(e)
        else:
            self.set.discard(e)
                
    def remove(self, e):
        if self._invert:
            self.set.add(e)
        else:
            self.set.remove(e)

    def __iter__(self):
        '''Return the set of elements, if possible.'''
        if self._invert:
            if self.universeIterator is None:
                raise InfiniteSetError()
            contains = self.set.__contains__
            for e in self.universeIterator:
                if not contains(e):
                    yield e
        else:
            for e in self.set:
                yield e

    def union(self, other):
        """It helps to draw a Venn diagram to understand what's going on
        here. It's very basic, with the only complication being that we
        have to consider which of two sets is inverted (i.e., complemented)."""
        if self._invert:
            if other._invert:
                self.set.intersection_update(other.set)
                return self
            else:
                self.set.difference_update(other.set)
                return self
        else:
            if other._invert:
                # Self normal, other inverted.
                
                # TODO: check to see if making difference_update repeatedly
                # check to see if its source set is empty makes it faster.
                # It is pretty dumb about just removing everything, even if
                # the source set has already been emptied.
                other.set.difference_update(self.set)
                return other
            else:
                # Both sets are normal.
                self.set.update(other.set)
                return self

    def intersection(self, other):
        """It helps to draw a Venn diagram to understand what's going on
        here. It's very basic, with the only complication being that we
        have to consider which of two sets is inverted (i.e.,
        complemented)."""
        if self._invert:
            if other._invert:
                self.set.update(other.set)
                return self
            else:
                other.set.difference_update(self.set)
                return other
        else:
            if other._invert:
                # Self normal, other inverted. This clobbers other.
                
                # TODO: check to see if making difference_update repeatedly
                # check to see if its source set is empty makes it
                # faster. It is pretty dumb about just removing everything,
                # even if the source set has already been emptied.
                self.set.difference_update(other.set)
                return self
            else:
                # Both sets are normal.
                self.set.intersection_update(other.set)
                return self
