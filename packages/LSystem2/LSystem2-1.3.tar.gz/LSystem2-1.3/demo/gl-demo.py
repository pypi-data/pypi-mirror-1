#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: gl-demo.py 66 2005-11-26 09:04:10Z const $"

gl = LSystem2.GL(color = (0, 0, 0.1, 0), fullscreen = True)

L = LSystem2.LSystem(3)
L.production = (1, 0, 0), (0, 1, 0), (0, 0, 1)
L.state = (0, 2, 0), (0, -2, 0)
L.zero = (0, -1, 0)
L.depth = 7
gl.append(L)

gl.mainloop()
