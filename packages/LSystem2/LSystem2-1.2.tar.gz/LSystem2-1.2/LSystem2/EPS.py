#!/usr/bin/env python
from Complex import *

__revision__ = "$Id: EPS.py 12 2005-07-10 18:43:27Z const $"

class EPS(list):

    __slots__ = "__bbox"

    def __new__(cls):
        new = list.__new__(cls)
        new.__bbox = None
        return new

    def append(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(v, "__iter__"):
                v = v,
            list.append(self, "%s%s\n" % (
                str.join("", map(lambda v: "%s\t" % v, v)), k,
                ))

    def stroke(self, L, **kwargs):
        list.append(self, "gsave\n")
        list.append(self, "newpath\n")
        self.append(**kwargs)
        list.append(self, "%g\t%g\tmoveto\n" % L.zero)
        self.extend(map(lambda z: "%g\t%g\tlineto\n" % z[:2], L))
        if self.__bbox is None:
            self.__bbox = [Complex(L.power, z) for z in L.bounds]
        else:
            for z in L.bounds:
                adjust_bounds(self.__bbox, Complex(L.power, z))
        list.append(self, "stroke\n")
        list.append(self, "grestore\n")

    def write(self, f, **kwargs):
        prop = {
            "title": "LSystem Fractal",
            }
        prop.update(kwargs)
        if self.__bbox is None:
            bbox = 0, 0, 0, 0
        else:
            bbox = self.__bbox[0].tuple() + self.__bbox[1].tuple()
        f.write("%!PS-Adobe-3.0 EPSF 3.0\n")
        f.write("%%%%Creator: %s\n" % __name__)
        f.write("%%%%Title: %s\n" % prop["title"])
        f.write("%%%%BoundingBox:\t\t%.f\t%.f\t%.f\t%.f\n" % bbox)
        f.write("%%%%HiResBoundingBox:\t%g\t%g\t%g\t%g\n" % bbox)
        map(f.write, self)
        f.write("showpage\n")
        f.write("%%EOF\n")
