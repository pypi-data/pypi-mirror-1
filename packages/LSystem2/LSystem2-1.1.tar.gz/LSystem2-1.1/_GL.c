#include <Python.h>
#include <structmember.h>
#include <GL/glut.h>

typedef struct {
  PyObject_HEAD;
  unsigned long l;
  PyObject **L;
  double distance;
  PyObject *color;
} GLObject;

static PyTypeObject GL_Type;
static GLObject *_ = NULL;

static GLObject *GL_new(PyTypeObject *type){
  GLObject *new;

  if(!PyType_IsSubtype(type, &GL_Type))
    goto fault0;
  new = (GLObject *)type->tp_alloc(type, 0);
  if(new == NULL)
    goto fault0;
  new->l = 0;
  new->L = PyMem_New(PyObject *, 0);
  if(new->L == NULL)
    goto fault1;
  new->color = NULL;
  new->distance = 3;
  return new;

 fault1:
  type->tp_free(new);
 fault0:
  return NULL;
}

static void GL_dealloc(GLObject *self){
  PyMem_Free(self->L);
  self->ob_type->tp_free(self);
}

static PyObject *GL_append(GLObject *self, PyObject *L){
  PyObject **p;

  p = PyMem_Resize(self->L, PyObject *, self->l + 1);
  if(p == NULL)
    goto fault0;
  Py_INCREF(L);
  p[self->l++] = L;
  self->L = p;
  Py_INCREF(Py_None);
  return Py_None;

 fault0:
  return NULL;
}

static double _time(void){
  static PyObject *timefunc = NULL;
  PyObject *r;
  double t;

  if(timefunc == NULL){
    PyObject *timemodule;

    timemodule = PyImport_ImportModule("time");
    if(timemodule == NULL)
      goto fault0;
    timefunc = PyObject_GetAttrString(timemodule, "time");
    Py_DECREF(timemodule);
    if(timefunc == NULL)
      goto fault0;
  }
  r = PyObject_CallFunction(timefunc, NULL);
  if(r == NULL)
    goto fault0;
  t = PyFloat_AsDouble(r);
  if(PyErr_Occurred() != NULL)
    goto fault0;
  Py_DECREF(r);
  return t;

 fault0:
  PyErr_Clear();
  return 0;
}

static void _display(void){
  PyObject **p;
  double t;

  t = _time();
  glClear(GL_COLOR_BUFFER_BIT);
  glLoadIdentity();
  glTranslated(0, 0, -_->distance);
  for(p = _->L; p - _->L < _->l; p++){
    PyObject *iter, *color, *speed, *axis;
    double a, s;

    iter = PyObject_GetIter(*p);
    if(iter == NULL)
      goto fault0;
    color = PyObject_GetAttrString(*p, "color");
    if(color != NULL){
      double v[3];
      int i;

      for(i = 0; i < 3; i++){
	PyObject *item;

	item = PySequence_GetItem(color, i);
	if(item == NULL)
	  goto fault2;
	v[i] = PyFloat_AsDouble(item);
	if(PyErr_Occurred() != NULL)
	  goto fault2;
	continue;

      fault2:
	PyErr_Clear();
	v[i] = 1;
      }
      Py_DECREF(color);
      glColor3d(v[0], v[1], v[2]);
    }else{
      PyErr_Clear();
      glColor3d(1, 1, 1);
    }
    s = 120;
    speed = PyObject_GetAttrString(*p, "speed");
    if(speed != NULL){
      double _s;

      _s = PyFloat_AsDouble(speed);
      Py_DECREF(speed);
      if(PyErr_Occurred() == NULL)
	s = _s;
    }else
      PyErr_Clear();
    a = t * s;
    a -= (long long)(a / 360) * 360;
    glPushMatrix();
    axis = PyObject_GetAttrString(*p, "axis");
    if(axis != NULL){
      double v[3];
      int i;

      for(i = 0; i < 3; i++){
	PyObject *item;

	item = PySequence_GetItem(axis, i);
	if(item == NULL)
	  goto fault3;
	v[i] = PyFloat_AsDouble(item);
	Py_DECREF(item);
	if(PyErr_Occurred() != NULL)
	  goto fault3;
	continue;

      fault3:
	PyErr_Clear();
	v[i] = (i == 1) ? 1 : 0;
	continue;
      }
      Py_DECREF(axis);
      glRotated(a, v[0], v[1], v[2]);
    }else{
      PyErr_Clear();
      glRotated(a, 0, 1, 0);
    }
    glBegin(GL_LINE_STRIP);
    for(;;){
      PyObject *z;
      int i;
      double v[3];

      z = PyIter_Next(iter);
      if(z == NULL){
	if(PyErr_Occurred() != NULL)
	  PyErr_Clear();
	break;
      }

      for(i = 0; i < 3; i++){
	PyObject *item;

	item = PySequence_GetItem(z, i);
	if(item == NULL)
	  if(i == 0)
	    goto fault1;
	  else{
	    PyErr_Clear();
	    v[i] = 0;
	    continue;
	  }
	v[i] = PyFloat_AsDouble(item);
	if(PyErr_Occurred() != NULL)
	  goto fault1;
	Py_DECREF(item);
	continue;

      fault1:
	Py_DECREF(item);
	break;
      }
      Py_DECREF(z);
      if(PyErr_Occurred() == NULL)
	glVertex3d(v[0], v[1], v[2]);
      else
	PyErr_Clear();
    }
    Py_DECREF(iter);
    glEnd();
    glPopMatrix();
    if(PyErr_Occurred() != NULL)
      goto fault0;
    continue;

  fault0:
    PyErr_Clear();
  }
  glutSwapBuffers();
}

static void _keyboard(unsigned char c, int x, int y){
  if(c == 27)
    Py_Exit(0);
}

static void _reshape(int width, int height){
  if(width > height)
    glViewport((width - height) / 2, 0, height, height);
  else
    glViewport(0, (height - width) / 2, width, width);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  if(_->distance < 1)
    glOrtho(-1, 1, -1, 1, -1, 1);
  else
    glFrustum(-1, 1, -1, 1, _->distance - 1, _->distance + 1);
  glMatrixMode(GL_MODELVIEW);
}

static PyObject *GL_mainloop(GLObject *self, PyObject *arg){
  PyObject *item;
  int argc, i;
  char **argv;

  if(_ != NULL)
    goto fault0;
  _ = self;
  argc = PySequence_Length(arg);
  if(argc < 1)
    goto fault0;
  argv = PyMem_New(char *, argc);
  if(argv == NULL)
    goto fault0;
  for(i = 0; i < argc; i++){
    item = PySequence_GetItem(arg, i);
    if(item == NULL)
      goto fault1;
    argv[i] = PyString_AsString(item);
    if(argv[i] == NULL)
      goto fault1;
  }
  glutInit(&argc, argv);
  glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
  glutCreateWindow(argv[0]);
  if(self->color != NULL){
    double v[4];
    int i;
    for(i = 0; i < 4; i++){
      item = PySequence_GetItem(self->color, i);
      if(item == NULL)
	goto fault2;
      v[i] = PyFloat_AsDouble(item);
      Py_DECREF(item);
      if(PyErr_Occurred() != NULL)
	goto fault2;
      continue;

    fault2:
      v[i] = 0;
    }
    glClearColor(v[0], v[1], v[2], v[3]);
  }else
    glClearColor(0, 0, 0, 0);
  glutFullScreen();
  glShadeModel(GL_FLAT);
  glutDisplayFunc(_display);
  glutIdleFunc(_display);
  glutKeyboardFunc(_keyboard);
  glutReshapeFunc(_reshape);
  glutMainLoop();
  PyMem_Free(argv);
  Py_INCREF(Py_None);
  return Py_None;

 fault1:
  PyMem_Free(argv);
 fault0:
  return NULL;
}

static PyMethodDef GL_methods[] = {
  {"append", (PyCFunction)GL_append, METH_O},
  {"mainloop", (PyCFunction)GL_mainloop, METH_O},
  {}
};

static PyMemberDef GL_members[] = {
  {"distance", T_DOUBLE, offsetof(GLObject, distance)},
  {"color", T_OBJECT, offsetof(GLObject, color)},
  {}
};

static PyTypeObject GL_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  .tp_name = "_GL.GL",
  .tp_basicsize = sizeof(GLObject),
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = (newfunc)GL_new,
  .tp_dealloc = (destructor)GL_dealloc,
  .tp_methods = GL_methods,
  .tp_members = GL_members,
};

static PyMethodDef _GL_methods[] = {
  {}
};

PyMODINIT_FUNC init_GL(void){
  PyObject *_GL;

  if(PyType_Ready(&GL_Type) == -1)
    goto fault0;
  _GL = Py_InitModule("_GL", _GL_methods);
  if(_GL == NULL)
    goto fault0;
  Py_INCREF(&GL_Type);
  PyModule_AddObject(_GL, "GL", (PyObject *)&GL_Type);
  PyModule_AddStringConstant(_GL, "__release__", "$Id: _GL.c 11 2005-07-05 18:33:59Z const $");
  return;

 fault0:
  return;
}
