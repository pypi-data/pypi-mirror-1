#!/usr/bin/env python

__revision__ = "$Id: __init__.py 66 2005-11-26 09:04:10Z const $"

from LSystem import LSystem
from EPS import EPS

try:
    from Tk import Tk
except ImportError:
    pass

try:
    from GL import GL
except ImportError:
    pass
