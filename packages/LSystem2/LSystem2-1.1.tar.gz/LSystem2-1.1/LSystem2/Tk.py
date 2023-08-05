#!/usr/bin/env python
import Tkinter

__revision__ = "$Id: Tk.py 11 2005-07-05 18:33:59Z const $"

class Tk(Tkinter.Tk):

    def __init__(self, *args, **kwargs):
        Tkinter.Tk.__init__(self)
        self._canvas = Tkinter.Canvas(*args, **kwargs)
        self._bbox = 0, 0

    def stroke(self, L, *args, **kwargs):
        self._canvas.create_line(list(L), *args, **kwargs)
        self._bbox = map(max, zip(self._bbox, L.bounds[1]))

    def mainloop(self, *args):
        self._canvas["width"], self._canvas["height"] = self._bbox
        self._canvas.pack()
        Tkinter.Tk.mainloop(self, *args)
