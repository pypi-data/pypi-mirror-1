#!/usr/bin/env python
from Quaternion import Quaternion

__revision__ = "$Id: LSystem.py 71 2005-12-04 20:08:21Z const $"

class LSystem(object):

    __slots__ = "production", "state", "zero", "depth", "__bounds"

    def __new__(cls):
        new = object.__new__(cls)
        new.__bounds = Quaternion(), Quaternion()
        new.production = (1,),
        new.state = (1,),
        new.zero = ()
        new.depth = 0
        return new

    def __getattribute__(self, attr):
        if attr == "bounds":
            return self.__bounds
        v = object.__getattribute__(self, attr)
        if attr in ["production", "state"]:
            return [q() for q in v]
        elif attr == "zero":
            return v()
        else:
            return v

    def __setattr__(self, attr, value):
        if attr in ["production", "state"]:
            v = [Quaternion(*x) for x in value]
            if attr == "production":
                _s = sum(v, Quaternion())
                v = [x / _s for x in v]
        elif attr == "zero":
            v = Quaternion(*value)
        elif attr == "depth":
            v = long(value)
        else:
            v = value
        object.__setattr__(self, attr, v)

    def __delattr__(self, attr):
        if attr in self.__slots__:
            raise AttributeError
        object.__delattr__(self, attr)

    def __process(self, u, depth):
        if depth > 0:
            for p in object.__getattribute__(self, "production"):
                for v in self.__process(u * p, depth - 1):
                    yield v
        else:
            yield u

    def __iter__(self):
        curr = object.__getattribute__(self, "zero")
        self.__bounds = curr, curr
        for u in object.__getattribute__(self, "state"):
            for v in self.__process(u, self.depth):
                curr += v
                self.__bounds = (curr & self.__bounds[0],
                                 curr | self.__bounds[1])
                yield curr()
