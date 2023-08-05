#!/usr/bin/env python

__revision__ = "$Id: EPS.py 8 2005-07-04 09:56:45Z const $"

class EPS(list):

    def __init__(self, extra = {}):
        list.__init__(self)
        self.extra = extra
        self.bbox = None

    def stroke(self, L, extra = {}):
        self.append("gsave\n")
        self.append("newpath\n")
        _extra = dict(self.extra)
        _extra.update(extra)
        for k, w in _extra.items():
            self.append("%s %s\n" % (
                (hasattr(w, "__iter__") and \
                 str.join(" ", map(str, tuple(w))) or \
                 str(w), k)))
        self.append("%g\t%g\tmoveto\n" % L.zero)
        self.extend(map(lambda z: "%g\t%g\tlineto\n" % z[:2], L))
        if self.bbox is None:
            self.bbox = L.bounds
        else:
            bbox = L.bounds
            self.bbox = (
                map(min, zip(self.bbox[0], bbox[0])),
                map(max, zip(self.bbox[1], bbox[1])),
                )
        self.append("stroke\n")
        self.append("grestore\n\n")

    def write(self, f, title = "LSystem"):
        f.write("%!PS-Adobe-3.0 EPSF 3.0\n")
        f.write("%%%%Title: %s\n" % title)
        if self.bbox is None:
            bbox = 0, 0, 0, 0
        else:
            bbox = tuple(self.bbox[0] + self.bbox[1])
        f.write("%%%%BoundingBox:\t\t%.f\t%.f\t%.f\t%.f\n" % bbox)
        f.write("%%%%HiResBoundingBox:\t%g\t%g\t%g\t%g\n" % bbox)
        map(f.write, self)
        f.write("showpage\n")
        f.write("%%EOF\n")
