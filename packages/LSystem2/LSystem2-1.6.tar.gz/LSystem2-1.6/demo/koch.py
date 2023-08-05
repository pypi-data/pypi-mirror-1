#!/usr/bin/env python
import LSystem2, math

__revision__ = "$Id: koch.py 87 2006-03-12 20:00:13Z const $"

D = 81

L = LSystem2.LSystem()
Q = LSystem2.Quaternion
L.production =(Q(1.0 / 3), Q.rotate(math.pi / 3, 0, 0, 1) / 3,
               Q.rotate(math.pi / 3, 0, 0, -1) / 3, Q(1.0 / 3))
L.state = Q(0, D, D * 3**0.5), Q(0, D, -D * 3**0.5), Q(0, -2 * D, 0)
L.depth = 5

eps = LSystem2.EPS(title = "Koch's Snowflakes")
eps.append(setlinewidth = 0.2, setlinejoin = 1)

eps.stroke(L, setrgbcolor = (0, 0, 0.6))

L.zero = Q(0, D * 7 / 3.0, 0)
eps.stroke(L, setrgbcolor = (0.8, 0, 0))

L.zero = Q(0, D * 7 / 6.0, -D * 3.5 / 3**0.5)
eps.stroke(L, setrgbcolor = (0, 0.7, 0))

eps.write(file("koch.eps", "w"))
