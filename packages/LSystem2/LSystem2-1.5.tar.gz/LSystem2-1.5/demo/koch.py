#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: koch.py 71 2005-12-04 20:08:21Z const $"

D = 81

L = LSystem2.LSystem()
L.production = (2, 0), (1, 3**0.5), (1, -3**0.5), (2, 0)
L.state = (D, D * 3**0.5), (D, -D * 3**0.5), (-2 * D, 0)
L.depth = 5

eps = LSystem2.EPS(title = "Koch's Snowflakes")
eps.append(setlinewidth = 0.2, setlinejoin = 1)

eps.stroke(L, setrgbcolor = (0, 0, 0.6))

L.zero = (D * 7 / 3.0, 0)
eps.stroke(L, setrgbcolor = (0.8, 0, 0))

L.zero = (D * 7 / 6.0, -D * 3.5 / 3**0.5)
eps.stroke(L, setrgbcolor = (0, 0.7, 0))

eps.write(file("koch.eps", "w"))
