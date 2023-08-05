#!/usr/bin/env python
import LSystem2, math

__revision__ = "$Id: tk-demo.py 87 2006-03-12 20:00:13Z const $"

D = 243

L = LSystem2.LSystem()
Q = LSystem2.Quaternion
L.production =(Q(1.0 / 3), Q.rotate(math.pi / 3, 0, 0, 1) / 3,
               Q.rotate(math.pi / 3, 0, 0, -1) / 3, Q(1.0 / 3))
L.state = Q(0, D * 2, 0), Q(0, -D, -D * 3**0.5), Q(0, -D, D * 3**0.5)
L.zero = Q(0, 0, D * 3**0.5)
L.depth = 6

T = LSystem2.Tk(background = "lightblue")
T.stroke(L, fill = "navy")
T.title("Koch's Snowflake")
T()
