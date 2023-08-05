#!/usr/bin/env python
import LSystem2, math

__revision__ = "$Id: sierpinsky.py 87 2006-03-12 20:00:13Z const $"

D = 128

L = LSystem2.LSystem()
Q = LSystem2.Quaternion
L.production = (Q(1), Q.rotate(math.pi * 2 / 3, 0, 0, 1) * 0.5,
                Q.rotate(math.pi * 2 / 3, 0, 0, -1) * 0.5, Q(0.5))
L.state = Q(0, 2 * D, 0), Q(0, -D, D * 3**0.5), Q(0, -D, -D * 3**0.5)
L.depth = 6

eps = LSystem2.EPS(title = "Sierpinsky's Tetrahedron")
eps.stroke(L, setlinewidth = 0.4, setrgbcolor = (0.4, 0.2, 0.6))
eps.write(file("sierpinsky.eps", "w"))
