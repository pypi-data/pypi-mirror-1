#!/usr/bin/env python
from Quaternion import Quaternion

__revision__ = "$Id: LSystem.py 87 2006-03-12 20:00:13Z const $"

class LSystem(object):

    __slots__ = "bounds", "depth", "production", "state", "zero"

    def __new__(cls):
        new = object.__new__(cls)
        new.bounds = Quaternion(), Quaternion()
        new.production = Quaternion(1),
        new.state = Quaternion(0, 1, 0, 0),
        new.zero = Quaternion()
        new.depth = 0
        return new

    def _process(self, depth):
        if depth > 0:
            for p in self.production:
                for q in self._process(depth - 1):
                    yield p * q
        else:
            yield Quaternion(1)

    def __iter__(self):
        curr = self.zero
        self.bounds = curr, curr
        for u in self.state:
            for q in self._process(self.depth):
                curr += q * u / q * Quaternion(abs(q))
                self.bounds = (curr & self.bounds[0], curr | self.bounds[1])
                yield curr
