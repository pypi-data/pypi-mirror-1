#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: demo.py 8 2005-07-04 09:56:45Z const $"

D = 128

eps = LSystem2.EPS({"setlinewidth": 0.2, "setlinejoin": 1})

# Sierpinsky's Tetrahedron
L = LSystem2.LSystem(2)
L.production = (4, 0), (-1, 3**0.5), (-1, -3**0.5), (2, 0)
L.state = (
    (D * 2, -D * 2 * 3**0.5),
    (D * 2, D * 2 * 3**0.5),
    (-D * 4, 0),
    )
L.build(8)
L.zero = (0, D * 2 * 3**0.5)
eps.stroke(L, {"setrgbcolor": (0.7, 0.7, 0.7)})

# Koch's Snowflake
L = LSystem2.LSystem(2)
L.production = (2, 0), (1, 3**0.5), (1, -3**0.5), (2, 0)
L.state = (2 * D, 0), (-D, -D * 3**0.5), (-D, D * 3**0.5)
L.build(5)
L.zero = (0, D * 2 * 3**0.5)
eps.stroke(L, {"setrgbcolor": (0.8, 0, 0)})
L.zero = (D * 2, D * 2 * 3**0.5)
eps.stroke(L, {"setrgbcolor": (0, 0, 0.7)})
L.zero = (D, D * 3**0.5)
eps.stroke(L, {"setrgbcolor": (0, 0.6, 0)})

eps.write(file("demo.eps", "w"), title = "LSystem2 Demo")
