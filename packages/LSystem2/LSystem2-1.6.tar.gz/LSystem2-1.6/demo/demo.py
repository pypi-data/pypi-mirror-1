#!/usr/bin/env python
import LSystem2, math

__revision__ = "$Id: demo.py 87 2006-03-12 20:00:13Z const $"

D = 128

eps = LSystem2.EPS(title = "LSystem Demo Fractals")
eps.append(setlinewidth = 0.2, setlinejoin = 1)
Q = LSystem2.Quaternion

# Sierpinsky's Tetrahedron
L = LSystem2.LSystem()
L.production = (Q(1), Q.rotate(math.pi * 2 / 3, 0, 0, 1) * 0.5,
                Q.rotate(math.pi * 2 / 3, 0, 0, -1) * 0.5, Q(0.5))
L.state = (
    Q(0, D * 2, -D * 2 * 3**0.5),
    Q(0, D * 2, D * 2 * 3**0.5),
    Q(0, -D * 4, 0),
    )
L.depth = 8
L.zero = Q(0, 0, D * 2 * 3**0.5, 0)
eps.stroke(L, setrgbcolor = (0.7, 0.7, 0.7))

# Koch's Snowflake
L = LSystem2.LSystem()
L.production =(Q(1.0 / 3), Q.rotate(math.pi / 3, 0, 0, 1) / 3,
               Q.rotate(math.pi / 3, 0, 0, -1) / 3, Q(1.0 / 3))
L.state = Q(0, 2 * D, 0), Q(0, -D, -D * 3**0.5), Q(0, -D, D * 3**0.5)
L.depth = 5
L.zero = Q(0, 0, D * 2 * 3**0.5)
eps.stroke(L, setrgbcolor = (0.8, 0, 0))
L.zero = Q(0, D * 2, D * 2 * 3**0.5)
eps.stroke(L, setrgbcolor = (0, 0, 0.7))
L.zero = Q(0, D, D * 3**0.5)
eps.stroke(L, setrgbcolor = (0, 0.6, 0))

eps.write(file("demo.eps", "w"))
