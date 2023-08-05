#!/usr/bin/env python

__revision__ = "$Id: __init__.py 10 2005-07-05 09:36:21Z const $"

from _LSystem import LSystem, __version__, __author__
from _GL import GL
from EPS import EPS
from Tk import Tk

class LSystem(LSystem):

    def build(self, depth):
        for i in xrange(int(depth)):
            self.step()
