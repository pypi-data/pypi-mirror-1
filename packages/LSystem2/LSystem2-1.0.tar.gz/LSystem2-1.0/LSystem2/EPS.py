#!/usr/bin/env python

__revision__ = "$Id: EPS.py 7 2005-07-02 06:11:11Z const $"

class EPS(list):

    def __init__(self):
        list.__init__(self)
        self._min = self._max = None

    def stroke(self, L, zero = (0.0, 0.0),
               linewidth = None, color = None, extra = []):
        if self._min is None:
            self._min = zero
            self._max = zero
        else:
            self._min = map(min, zip(self._min, zero))
            self._max = map(max, zip(self._max, zero))
        self.append("gsave\n")
        self.append("newpath\n")
        if linewidth:
            self.append("%s\tsetlinewidth\n" % linewidth)
        if color:
            self.append("%s\t%s\t%s\tsetrgbcolor\n" % color)
        self.extend(extra)
        self.append("%g\t%g\tmoveto\n" % zero)
        for v in L:
            v = zero[0] + v[0], zero[1] + v[1]
            self._min = map(min, zip(self._min, v))
            self._max = map(max, zip(self._max, v))
            self.append("%g\t%g\tlineto\n" % v)
        self.append("stroke\n")
        self.append("grestore\n\n")

    def write(self, f, title = "LSystem"):
        f.write("%!PS-Adobe-3.0 EPSF 3.0\n")
        f.write("%%%%Title: %s\n" % title)
        f.write("%%%%BoundingBox:\t\t%.f\t%.f\t%.f\t%.f\n" % (
            self._min[0], self._min[1], self._max[0], self._max[1],
            ))
        f.write("%%%%HiResBoundingBox:\t%g\t%g\t%g\t%g\n" % (
            self._min[0], self._min[1], self._max[0], self._max[1],
            ))
        for s in self:
            f.write(s)
        f.write("showpage\n")
        f.write("%%EOF\n")
