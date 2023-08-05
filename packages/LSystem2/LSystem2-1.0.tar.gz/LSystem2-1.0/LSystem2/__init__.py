#!/usr/bin/env python

__revision__ = "$Id: __init__.py 7 2005-07-02 06:11:11Z const $"

from _LSystem import LSystem, __version__, __author__
from EPS import EPS

class LSystem(LSystem):

    def build(self, depth):
        for i in xrange(int(depth)):
            self.step()
