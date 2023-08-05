#!/usr/bin/env python

__revision__ = "$Id: __init__.py 87 2006-03-12 20:00:13Z const $"

from LSystem import LSystem, Quaternion
from EPS import EPS

class _NotImplemented(object):

    def __new__(self, *args, **kwargs):
        raise NotImplementedError

try:
    from Tk import Tk
except ImportError:
    Tk = _NotImplemented

try:
    from GL import GL
except ImportError:
    GL = _NotImplemented
