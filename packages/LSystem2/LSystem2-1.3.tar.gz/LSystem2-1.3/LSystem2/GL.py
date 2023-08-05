#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
import sys, time

__revision__ = "$Id: GL.py 67 2005-11-27 17:31:07Z const $"

class GL(list):

    __slots__ = "__prop"

    def __init__(self, argv = sys.argv, **kwargs):
        list.__init__(self)
        self.__prop = dict(
            distance = 3,
            color = (0, 0, 0, 0),
            size = (800, 600),
            light0 = (1, 1, 0, 1),
            light1 = (1, 0.4, 1, 1),
            light2 = (0.2, 1, 1, 1),
            )
        self.__prop.update(kwargs)
        glutInit(argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutCreateWindow(argv[0])
        glutHideWindow()
        glClearColor(*self.__prop["color"])
        glEnable(GL_LIGHTING)
        for i in range(3):
            glEnable(GL_LIGHT0 + i)
            glLightfv(GL_LIGHT0 + i, GL_DIFFUSE, self.__prop["light%u" % i])
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, -1, 0))
        glLightfv(GL_LIGHT1, GL_POSITION, (-3**0.5, 0, 1, 0))
        glLightfv(GL_LIGHT2, GL_POSITION, (3**0.5, 0, 1, 0))
        glEnable(GL_DEPTH_TEST)
        glutDisplayFunc(self.__display)
        glutIdleFunc(glutPostRedisplay)
        glutReshapeFunc(self.__reshape)

    def append(self, L, **kwargs):
        if L.power != 3:
            raise RuntimeError
        prop = {
            "color": (1, 1, 1),
            "axis": (0, 1, 0),
            "speed": 120,
            }
        prop.update(kwargs)
        l = glGenLists(1)
        glNewList(l, GL_COMPILE)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, prop["color"])
        glBegin(GL_LINE_STRIP)
        glVertex3d(*L.zero)
        for z in L:
            glVertex3d(*z)
        glEnd()
        glEndList()
        list.append(self, (l, prop))

    def __display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        if self.__prop["distance"] > 1:
            glTranslated(0, 0, -self.__prop["distance"])
        for l, prop in self:
            glPushMatrix()
            glRotated(float(time.time()) * prop["speed"] % 360.0,
                      *prop["axis"])
            glCallList(l)
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

    def mainloop(self):
        glutShowWindow()
        if self.__prop["fullscreen"]:
            glutFullScreen()
        else:
            glutReshapeWindow(*self.__prop["size"])
        glutMainLoop()
