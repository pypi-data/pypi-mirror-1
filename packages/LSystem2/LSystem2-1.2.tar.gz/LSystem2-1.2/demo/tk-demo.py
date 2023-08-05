#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: tk-demo.py 12 2005-07-10 18:43:27Z const $"

D = 243

L = LSystem2.LSystem(2)
L.production = (2, 0), (1, 3**0.5), (1, -3**0.5), (2, 0)
L.state = (D * 2, 0), (-D, -D * 3**0.5), (-D, D * 3**0.5)
L.zero = (0, D * 3**0.5)
L.depth = 6

T = LSystem2.Tk(background = "lightblue")
T.stroke(L, fill = "navy")
T.title("Koch's Snowflake")
T.mainloop()
