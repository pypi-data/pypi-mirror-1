#!/usr/bin/env python
import Tkinter

__revision__ = "$Id: Tk.py 25 2005-09-28 12:39:03Z const $"

class Tk(Tkinter.Tk):

    def __init__(self, *args, **kwargs):
        Tkinter.Tk.__init__(self)
        self.__canvas = Tkinter.Canvas(*args, **kwargs)
        self.__bbox = 0, 0

    def stroke(self, L, **kwargs):
        if L.power != 2:
            raise RuntimeError
        self.__canvas.create_line(L.zero, *L, **kwargs)
        self.__bbox = map(max, zip(self.__bbox, L.bounds[1]))

    def mainloop(self, *args):
        self.__canvas["width"], self.__canvas["height"] = self.__bbox
        self.__canvas.pack()
        Tkinter.Tk.mainloop(self, *args)
