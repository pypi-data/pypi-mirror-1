#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: sierpinsky.py 8 2005-07-04 09:56:45Z const $"

D = 128

L = LSystem2.LSystem(2)
L.production = (4, 0), (-1, 3**0.5), (-1, -3**0.5), (2, 0)
L.state = (2 * D, 0), (-D, D * 3**0.5), (-D, -D * 3**0.5)
L.build(6)

eps = LSystem2.EPS()
eps.stroke(L, extra = {
    "setlinewidth": 0.4,
    "setrgbcolor": (0.4, 0.2, 0.6),
    })
eps.write(file("sierpinsky.eps", "w"), title = "Sierpinsky's Tetrahedron")
