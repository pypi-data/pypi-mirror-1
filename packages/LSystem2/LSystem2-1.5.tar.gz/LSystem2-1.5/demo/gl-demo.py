#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: gl-demo.py 72 2005-12-06 21:58:37Z const $"

gl = LSystem2.GL(color = (0, 0, 0.1, 0), title = "GL Demo")

L = LSystem2.LSystem()
L.production = (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)
L.state = (0, 1.2, 0, 0), (0, -1.2, 0, 0)
L.zero = (0, -0.6, 0, 0)
L.depth = 9
gl.append(L)

gl()
