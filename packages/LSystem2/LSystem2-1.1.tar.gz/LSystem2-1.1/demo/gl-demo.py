#!/usr/bin/env python
import LSystem2, sys

__revision__ = "$Id: gl-demo.py 11 2005-07-05 18:33:59Z const $"

S = LSystem2.LSystem(3)
S.production = (2, 0), (-1, 3**0.5), (2, 0), (-1, -3**0.5), (2, 0)
S.state = (0, 0, 3**0.5),
S.zero = (0, -0.5, -3**0.5 / 2)
S.build(6)
S.color = 1, 0.9, 0.9
S.speed = 60

K = LSystem2.LSystem(3)
K.production = (2, 0), (1, 3**0.5), (1, -3**0.5), (2, 0)
K.state = (3**0.5 / 2, 1.5), (3**0.5 / 2, -1.5), (-3**0.5, 0)
K.zero = (-3**0.5 / 2, -0.5)
K.build(6)
K.color = 0.9, 1, 0.9
K.axis = 1, 1, 1
K.speed = -30

gl = LSystem2.GL()
gl.append(S)
gl.append(K)
gl.color = 0, 0, 0.1
gl.mainloop(sys.argv)
