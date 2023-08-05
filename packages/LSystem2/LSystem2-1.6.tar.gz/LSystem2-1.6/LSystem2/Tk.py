#!/usr/bin/env python
import Tkinter

__revision__ = "$Id: Tk.py 87 2006-03-12 20:00:13Z const $"

class Tk(Tkinter.Tk):

    def __init__(self, *args, **kwargs):
        Tkinter.Tk.__init__(self)
        self.__canvas = Tkinter.Canvas(*args, **kwargs)
        self.__bbox = None

    def stroke(self, L, **kwargs):
        self.__canvas.create_line((L.zero[1], L.zero[2]),
                                  [(q[1], q[2]) for q in L], **kwargs)
        if self.__bbox is None:
            self.__bbox = L.bounds[1]
        else:
            self.__bbox |= L.bounds[1]

    def __call__(self, *args):
        if self.__bbox is not None:
            self.__canvas["width"] = self.__bbox[1]
            self.__canvas["height"] = self.__bbox[2]
        self.__canvas.pack()
        return self.mainloop(*args)
