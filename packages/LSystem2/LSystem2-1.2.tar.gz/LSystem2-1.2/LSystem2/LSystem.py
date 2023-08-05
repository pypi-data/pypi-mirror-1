#!/usr/bin/env python
from Complex import *

__revision__ = "$Id: LSystem.py 13 2005-07-10 18:46:48Z const $"

class LSystem(object):

    __slots__ = (
        "production", "state",
        "zero", "depth",
        "__power", "__bounds",
        )

    def __new__(cls, power):
        new = object.__new__(cls)
        new.__power = long(power)
        new.__bounds = Complex(new.__power, ()), Complex(new.__power, ())
        new.production = (1,),
        new.state = (1,),
        new.zero = ()
        new.depth = 0
        return new

    def __getattribute__(self, attr):
        if attr == "bounds":
            return map(Complex.tuple, self.__bounds)
        elif attr == "power":
            return self.__power
        v = object.__getattribute__(self, attr)
        if attr in ["production", "state"]:
            return map(Complex.tuple, v)
        elif attr == "zero":
            return v.tuple()
        else:
            return v

    def __setattr__(self, attr, value):
        if attr in ["production", "state"]:
            v = [Complex(self.__power, x) for x in value]
            if attr == "production":
                _s = sum(v, Complex(self.__power, ()))
                v = [x / _s for x in v]
        elif attr == "zero":
            v = Complex(self.__power, value)
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
        curr = object.__getattribute__(self, "zero").copy()
        self.__bounds = curr.copy(), curr.copy()
        for u in object.__getattribute__(self, "state"):
            for v in self.__process(u, self.depth):
                curr += v
                adjust_bounds(self.__bounds, curr)
                yield curr.tuple()
