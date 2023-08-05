#!/usr/bin/env python
import LSystem2, math

__revision__ = "$Id: gl-demo.py 87 2006-03-12 20:00:13Z const $"

gl = LSystem2.GL(color = (0, 0, 0.1, 0), title = "GL Demo")

Q = LSystem2.Quaternion
L = LSystem2.LSystem()
k = 3 ** -0.5
L.production = (Q.rotate(math.pi / 6, 0, -1, 0) * k,
                Q.rotate(math.pi / 2, 0, 1, 2) * k,
                Q.rotate(math.pi / 2, 0, 1, -2) * k,
                Q.rotate(math.pi / 6, 0, -1, 0) * k)
L.state = Q(0, 0.5, 0, 0),
L.zero = Q(0, -0.5, -0.3, -0.8)
L.depth = 6

gl.append(L)

gl()
