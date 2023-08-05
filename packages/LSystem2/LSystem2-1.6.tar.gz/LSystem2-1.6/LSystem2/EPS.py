#!/usr/bin/env python
from Quaternion import Quaternion

__revision__ = "$Id: EPS.py 87 2006-03-12 20:00:13Z const $"

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
            try:
                v = iter(v)
            except TypeError:
                v = (v,)
            list.append(self, "%s\t%s\n" % (
                str.join("\t", (str(x) for x in v)), k,
                ))

    def stroke(self, L, **kwargs):
        list.append(self, "gsave\n")
        list.append(self, "newpath\n")
        self.append(**kwargs)
        list.append(self, "%g\t%g\tmoveto\n" % (L.zero[1], L.zero[2]))
        self.extend("%g\t%g\tlineto\n" % (q[1], q[2]) for q in L)
        if self.__bbox is None:
            self.__bbox = L.bounds
        else:
            for z in L.bounds:
                self.__bbox = (self.__bbox[0] & z, self.__bbox[1] | z)
        list.append(self, "stroke\n")
        list.append(self, "grestore\n")

    def write(self, f):
        if self.__bbox is None:
            bbox = 0, 0, 0, 0
        else:
            bbox = (self.__bbox[0][1], self.__bbox[0][2],
                    self.__bbox[1][1], self.__bbox[1][2])
        f.write("%!PS-Adobe-3.0 EPSF 3.0\n")
        f.write("%%%%Creator: %s\n" % __name__)
        f.write("%%%%Title: %s\n" % self.__prop["title"])
        f.write("%%%%BoundingBox:\t\t%.f\t%.f\t%.f\t%.f\n" % bbox)
        f.write("%%%%HiResBoundingBox:\t%g\t%g\t%g\t%g\n" % bbox)
        for s in self:
            f.write(s)
        f.write("showpage\n")
        f.write("%%EOF\n")
