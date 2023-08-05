#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
import sys, time

__revision__ = "$Id: GL.py 13 2005-07-10 18:46:48Z const $"

class GL(list):

    __slots__ = "__prop"

    def __new__(cls):
        new = list.__new__(cls)
        new.__prop = {
            "distance": 3,
            "color": (0, 0, 0, 0),
            "shape": (800, 600),
            }
        return new

    def append(self, L, **kwargs):
        prop = {
            "color": (1, 1, 1),
            "axis": (0, 1, 0),
            "speed": 120,
            }
        prop.update(kwargs)
        if L.power != 3:
            raise RuntimeError
        list.append(self, (tuple(L), L.zero, prop))

    def __display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        if self.__prop["distance"] > 1:
            glTranslated(0, 0, -self.__prop["distance"])
        for L, zero, prop in self:
            glPushMatrix()
            glRotated(float(time.time()) * prop["speed"] % 360, *prop["axis"])
            glColor3d(*prop["color"])
            glBegin(GL_LINE_STRIP)
            glVertex3d(*zero)
            for z in L:
                glVertex3d(*z)
            glEnd()
            glPopMatrix()
        glutSwapBuffers()

    def __reshape(self, width, height):
        if(width > height):
            glViewport((width - height) / 2, 0, height, height)
        else:
            glViewport(0, (height - width) / 2, width, width)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        d = self.__prop["distance"]
        if d > 1:
            glFrustum(-1, 1, -1, 1, d - 1, d + 1)
        else:
            glOrtho(-1, 1, -1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def mainloop(self, argv = sys.argv, **kwargs):
        self.__prop.update(kwargs)
        glutInit(argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutCreateWindow(argv[0])
        glClearColor(*self.__prop["color"])
        glutDisplayFunc(self.__display)
        glutIdleFunc(glutPostRedisplay)
        glutReshapeFunc(self.__reshape)
        glutReshapeWindow(*self.__prop["shape"])
        glutMainLoop()
