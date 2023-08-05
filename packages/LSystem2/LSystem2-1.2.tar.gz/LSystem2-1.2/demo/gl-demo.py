#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: gl-demo.py 12 2005-07-10 18:43:27Z const $"

gl = LSystem2.GL()

L = LSystem2.LSystem(3)
L.production = (1, 0, 0), (0, 1, 0), (0, 0, 1)
L.state = (0, 2, 0), (0, -2, 0)
L.zero = (0, -1, 0)
L.depth = 8
gl.append(L, color = (0.9, 0.9, 1))

gl.mainloop(color = (0, 0, 0.1, 0))
