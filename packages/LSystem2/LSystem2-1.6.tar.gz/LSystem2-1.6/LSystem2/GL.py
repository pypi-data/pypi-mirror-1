#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
import sys, time

__revision__ = "$Id: GL.py 87 2006-03-12 20:00:13Z const $"

class GL(list):

    __slots__ = "__prop", "__fc"

    def __init__(self, argv = sys.argv, **kwargs):
        list.__init__(self)
        self.__prop = dict(
            distance = 3,
            color = (0, 0, 0, 0),
            size = (800, 600),
            )
        self.__prop.update(kwargs)
        glutInit(argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutCreateWindow(self.__prop.setdefault("title", argv[0]))
        glClearColor(*self.__prop["color"])
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_FOG)
        glFogf(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, self.__prop["distance"] - 1)
        glFogf(GL_FOG_END, self.__prop["distance"] + 2)
        glFogf(GL_FOG_DENSITY, 0.2)
        glutDisplayFunc(self.__display)
        glutIdleFunc(glutPostRedisplay)
        glutReshapeFunc(self.__reshape)

    def append(self, L, **kwargs):
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
        glVertex3d(L.zero[1], L.zero[2], L.zero[3])
        for q in L:
            glVertex3d(q[1], q[2], q[3])
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
        self.__fc[0] += 1

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

    def __timer(self, value = None):
        t = time.time()
        if value is not None:
            [f, c] = self.__fc
            glutSetWindowTitle("%s [%.1f fps]" % (self.__prop["title"],
                                                  f / (t - c)))
        self.__fc = [0, t]
        glutTimerFunc(1000, self.__timer, 0)

    def __call__(self):
        if self.__prop.get("fullscreen"):
            glutFullScreen()
        else:
            glutReshapeWindow(*self.__prop["size"])
        self.__timer(None)
        glutMainLoop()
