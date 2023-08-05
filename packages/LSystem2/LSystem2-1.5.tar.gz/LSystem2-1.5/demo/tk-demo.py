#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: tk-demo.py 71 2005-12-04 20:08:21Z const $"

D = 243

L = LSystem2.LSystem()
L.production = (2, 0), (1, 3**0.5), (1, -3**0.5), (2, 0)
L.state = (D * 2, 0), (-D, -D * 3**0.5), (-D, D * 3**0.5)
L.zero = (0, D * 3**0.5)
L.depth = 6

T = LSystem2.Tk(background = "lightblue")
T.stroke(L, fill = "navy")
T.title("Koch's Snowflake")
T()
