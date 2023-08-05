#!/usr/bin/env python
from Quaternion import Quaternion

__revision__ = "$Id: EPS.py 71 2005-12-04 20:08:21Z const $"

class EPS(list):

    __slots__ = "__bbox", "__prop"

    def __init__(self, **kwargs):
        list.__init__(self)
        self.__bbox = None
        self.__prop = {
            "title": "LSystem Fractal",
            }
        self.__prop.update(kwargs)

    def append(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(v, "__iter__"):
                v = v,
            list.append(self, "%s%s\n" % (
                str.join("", ("%s\t" % x for x in v)), k,
                ))

    def stroke(self, L, **kwargs):
        list.append(self, "gsave\n")
        list.append(self, "newpath\n")
        self.append(**kwargs)
        list.append(self, "%g\t%g\tmoveto\n" % (L.zero[0], L.zero[1]))
        self.extend("%g\t%g\tlineto\n" % (q[0], q[1]) for q in L)
        if self.__bbox is None:
            self.__bbox = L.bounds
        else:
            for z in L.bounds:
                self.__bbox = z & self.__bbox[0], z | self.__bbox[1]
        list.append(self, "stroke\n")
        list.append(self, "grestore\n")

    def write(self, f):
        if self.__bbox is None:
            bbox = 0, 0, 0, 0
        else:
            bbox = (self.__bbox[0][0], self.__bbox[0][1],
                    self.__bbox[1][0], self.__bbox[1][1])
        f.write("%!PS-Adobe-3.0 EPSF 3.0\n")
        f.write("%%%%Creator: %s\n" % __name__)
        f.write("%%%%Title: %s\n" % self.__prop["title"])
        f.write("%%%%BoundingBox:\t\t%.f\t%.f\t%.f\t%.f\n" % bbox)
        f.write("%%%%HiResBoundingBox:\t%g\t%g\t%g\t%g\n" % bbox)
        for s in self:
            f.write(s)
        f.write("showpage\n")
        f.write("%%EOF\n")
