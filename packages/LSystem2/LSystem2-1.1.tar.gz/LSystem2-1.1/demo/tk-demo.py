#!/usr/bin/env python
import LSystem2

__revision__ = "$Id: tk-demo.py 9 2005-07-04 17:53:35Z const $"

D = 243

L = LSystem2.LSystem(2)
L.production = (2, 0), (1, 3**0.5), (1, -3**0.5), (2, 0)
L.state = (D * 2, 0), (-D, -D * 3**0.5), (-D, D * 3**0.5)
L.zero = (0, D * 3**0.5)
L.build(7)

T = LSystem2.Tk()
T.stroke(L)
T.title("Koch's Snowflake")
T.mainloop()
