#!/usr/bin/env python
import Tkinter

__revision__ = "$Id: Tk.py 71 2005-12-04 20:08:21Z const $"

class Tk(Tkinter.Tk):

    def __init__(self, *args, **kwargs):
        Tkinter.Tk.__init__(self)
        self.__canvas = Tkinter.Canvas(*args, **kwargs)
        self.__bbox = None

    def stroke(self, L, **kwargs):
        self.__canvas.create_line((L.zero[0], L.zero[1]),
                                  [(q[0], q[1]) for q in L], **kwargs)
        if self.__bbox is None:
            self.__bbox = L.bounds[1]
        else:
            self.__bbox |= L.bounds

    def __call__(self, *args):
        if self.__bbox is not None:
            self.__canvas["width"] = self.__bbox[0]
            self.__canvas["height"] = self.__bbox[1]
        self.__canvas.pack()
        Tkinter.Tk.mainloop(self, *args)
