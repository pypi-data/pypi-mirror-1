#include <Python.h>

#ifndef VERSION
#define VERSION (__DATE__ " " __TIME__)
#endif

#ifndef AUTHOR
#define AUTHOR ""
#endif

typedef struct {
  PyObject_HEAD;
  unsigned long power;
  unsigned long lp, ls;
  double *p, *s;
} LSystemObject;

typedef struct {
  PyObject_HEAD;
  LSystemObject *self;
  double *p, *s;
} LSystemIteratorObject;

typedef struct {
  PyObject_HEAD;
  LSystemObject *self;
  unsigned long n;
  double *p;
} LSystemVIteratorObject;

static PyTypeObject LSystem_Type;
static PyTypeObject LSystemIterator_Type;
static PyTypeObject LSystemVIterator_Type;

static LSystemObject *LSystem_new(PyTypeObject *type, PyObject *args){
  LSystemObject *new;
  PyObject *arg, *power;
  if(!PyType_IsSubtype(type, &LSystem_Type))
    goto fault0;
  new = (LSystemObject *)type->tp_alloc(type, 0);
  if(new == NULL)
    goto fault0;
  arg = PySequence_GetItem(args, 0);
  if(arg == NULL)
    goto fault1;
  power = PyNumber_Long(arg);
  Py_DECREF(arg);
  if(power == NULL)
    goto fault1;
  new->power = PyLong_AsUnsignedLong(power);
  Py_DECREF(power);
  if(new->power == 0)
    goto fault1;
  new->ls = 0;
  new->s = PyMem_New(double, 0);
  if(new->s == NULL)
    goto fault1;
  new->lp = 0;
  new->p = PyMem_New(double, 0);
  if(new->p == NULL)
    goto fault2;
  return new;

 fault2:
  PyMem_Free(new->s);
 fault1:
  type->tp_free(new);
 fault0:
  return NULL;
}

static void LSystem_dealloc(LSystemObject *self){
  PyMem_Free(self->p);
  PyMem_Free(self->s);
  self->ob_type->tp_free(self);
}

static LSystemIteratorObject *LSystem_iter(LSystemObject *self){
  LSystemIteratorObject *iter;
  double *p;
  iter = PyObject_New(LSystemIteratorObject, &LSystemIterator_Type);
  if(iter == NULL)
    goto fault0;
  Py_INCREF(self);
  iter->self = self;
  iter->s = PyMem_New(double, self->power);
  if(iter->s == NULL)
    goto fault1;
  for(p = iter->s; p - iter->s < self->power; *p++ = 0);
  iter->p = self->s;
  return iter;

 fault1:
  PyObject_Del(iter);
 fault0:
  return NULL;
}

static LSystemVIteratorObject *LSystem_get_state(LSystemObject *self){
  LSystemVIteratorObject *iter;
  iter = PyObject_New(LSystemVIteratorObject, &LSystemVIterator_Type);
  if(iter == NULL)
    goto fault0;
  Py_INCREF(self);
  iter->self = self;
  iter->n = self->ls;
  iter->p = self->s;
  return iter;

 fault0:
  return NULL;
}

static int LSystem_set_state(LSystemObject *self, PyObject *value){
  int ls, i;
  double *s, *p;
  if(!PySequence_Check(value))
    goto fault0;
  ls = PySequence_Length(value);
  if(ls == -1)
    goto fault0;
  s = PyMem_New(double, ls * self->power);
  if(s == NULL)
    goto fault0;
  for(p = s, i = 0; i < ls; i++){
    PyObject *v;
    int j;
    v = PySequence_GetItem(value, i);
    if(!PySequence_Check(v))
      goto fault1;
    for(j = 0; j < self->power; j++){
      PyObject *item, *f;
      item = PySequence_GetItem(v, j);
      if(item == NULL)
	goto fault1;
      f = PyNumber_Float(item);
      Py_DECREF(item);
      if(f == NULL)
	goto fault1;
      p[j] = PyFloat_AsDouble(f);
      Py_DECREF(f);
    }
    p += self->power;
    continue;

  fault1:
    Py_XDECREF(v);
    PyMem_Free(s);
    goto fault0;
  }
  PyMem_Free(self->s);
  self->ls = ls;
  self->s = s;
  return 0;

 fault0:
  return -1;
}

static LSystemVIteratorObject *LSystem_get_production(LSystemObject *self){
  LSystemVIteratorObject *iter;
  iter = PyObject_New(LSystemVIteratorObject, &LSystemVIterator_Type);
  if(iter == NULL)
    goto fault0;
  Py_INCREF(self);
  iter->self = self;
  iter->n = self->lp;
  iter->p = self->p;
  return iter;

 fault0:
  return NULL;
}

static int LSystem_set_production(LSystemObject *self, PyObject *value){
  int lp, i;
  double *p, *s, *pp;
  if(!PySequence_Check(value))
    goto fault0;
  lp = PySequence_Length(value);
  if(lp == -1)
    goto fault0;
  s = PyMem_New(double, self->power);
  if(s == NULL)
    goto fault0;
  for(i = 0; i < self->power; s[i++] = 0);
  p = PyMem_New(double, lp * self->power);
  if(p == NULL)
    goto fault1;
  for(pp = p, i = 0; i < lp; i++){
    PyObject *v;
    int j;
    v = PySequence_GetItem(value, i);
    if(!PySequence_Check(v))
      goto fault2;
    for(j = 0; j < self->power; j++){
      PyObject *item, *f;
      item = PySequence_GetItem(v, j);
      if(item == NULL)
	goto fault2;
      f = PyNumber_Float(item);
      Py_DECREF(item);
      if(f == NULL)
	goto fault2;
      pp[j] = PyFloat_AsDouble(f);
      Py_DECREF(f);
      s[j] += pp[j];
    }
    pp += self->power;
    continue;

  fault2:
    Py_XDECREF(v);
    PyMem_Free(p);
    goto fault1;
  }
  switch(self->power){
  case 1:
    if(fabs(s[0]) < __DBL_EPSILON__)
      goto fault3;
    for(pp = p; pp - p < lp * self->power; pp += self->power){
      pp[0] /= s[0];
    }
    break;
  case 2: {
    double S = s[0] * s[0] + s[1] * s[1];
    if(fabs(S) < __DBL_EPSILON__)
      goto fault3;
    for(pp = p; pp - p < lp * self->power; pp += self->power){
      double tmp = (s[0] * pp[0] + s[1] * pp[1]) / S;
      pp[1] = (s[0] * pp[1] - s[1] * pp[0]) / S;
      pp[0] = tmp;
    }
    break;
  }
  case 3: {
    double S_12 = s[1] * s[1] + s[2] * s[2];
    if(fabs(S_12) < __DBL_EPSILON__){
      if(fabs(s[0]) < __DBL_EPSILON__)
	goto fault3;
      for(pp = p; pp - p < lp * self->power; pp += self->power){
	pp[0] /= s[0];
	pp[1] /= s[0];
	pp[2] /= s[0];
      }
    }else{
      double S2, S, a_22, a_23, a_33;
      S2 = s[0] * s[0] + S_12;
      S = sqrt(S2);
      a_22 = (s[0] * s[1] * s[1] + s[2] * s[2] * S) / S_12;
      a_23 = s[1] * s[2] * (s[0] - S) / S_12;
      a_33 = (s[0] * s[2] * s[2] + s[1] * s[1] * S) / S_12;
      for(pp = p; pp - p < lp * self->power; pp += self->power){
	double tmp[2];
	tmp[0] = (s[0] * pp[0] + s[1] * pp[1] + s[2] * pp[2]) / S2;
	tmp[1] = (-s[1] * pp[0] + a_22 * pp[1] + a_23 * pp[2]) / S2;
	pp[2] = (-s[2] * pp[0] + a_23 * pp[1] + a_33 * pp[2]) / S2;
	pp[0] = tmp[0];
	pp[1] = tmp[1];
      }
    }
    break;
  }
  default:
    PyErr_SetString(PyExc_RuntimeError, "not implemented");
    goto fault3;
  }
  PyMem_Free(s);
  PyMem_Free(self->p);
  self->lp = lp;
  self->p = p;
  return 0;

 fault3:
  PyMem_Free(p);
 fault1:
  PyMem_Free(s);
 fault0:
  return -1;
}

static PyObject *LSystem_step(LSystemObject *self){
  double *s, *p, *ps;
  s = PyMem_New(double, self->ls * self->power * self->lp);
  if(s == NULL)
    goto fault0;
  switch(self->power){
  case 1:
    for(p = s, ps = self->s; ps - self->s < self->ls * self->power; ps += self->power){
      double *pp;
      for(pp = self->p; pp - self->p < self->ls * self->power; pp += self->power, p += self->power){
	p[0] = ps[0] * pp[0];
      }
    }
    break;
  case 2:
    for(p = s, ps = self->s; ps - self->s < self->ls * self->power; ps += self->power){
      double *pp;
      for(pp = self->p; pp - self->p < self->lp * self->power; pp += self->power, p += self->power){
	p[0] = ps[0] * pp[0] - ps[1] * pp[1];
	p[1] = ps[1] * pp[0] + ps[0] * pp[1];
      }
    }
    break;
  case 3:
    for(p = s, ps = self->s; ps - self->s < self->ls * self->power; ps += self->power){
      double *pp, V_12;
      V_12 = ps[1] * ps[1] + ps[2] * ps[2];
      if(fabs(V_12) < __DBL_EPSILON__){
	for(pp = self->p; pp - self->p < self->lp * self->power; pp += self->power, p += self->power){
	  p[0] = ps[0] * pp[0];
	  p[1] = ps[0] * pp[1];
	  p[2] = ps[0] * pp[2];
	}
      }else{
	double V, a_22, a_23, a_33;
	V = sqrt(ps[0] * ps[0] + V_12);
	a_22 = (ps[0] * ps[1] * ps[1] + ps[2] * ps[2] * V) / V_12;
	a_23 = ps[1] * ps[2] * (ps[0] - V) / V_12;
	a_33 = (ps[0] * ps[2] * ps[2] + ps[1] * ps[1] * V) / V_12;
	for(pp = self->p; pp - self->p < self->lp * self->power; pp += self->power, p += self->power){
	  p[0] = ps[0] * pp[0] - ps[1] * pp[1] - ps[2] * pp[2];
	  p[1] = ps[1] * pp[0] + a_22 * pp[1] + a_23 * pp[2];
	  p[2] = ps[2] * pp[0] + a_23 * pp[1] + a_33 * pp[2];
	}
      }
    }
    break;
  default:
    PyErr_SetString(PyExc_RuntimeError, "not implemented");
    goto fault1;
  }
  PyMem_Free(self->s);
  self->ls *= self->lp;
  self->s = s;
  Py_INCREF(Py_None);
  return Py_None;

 fault1:
  PyMem_Free(s);
 fault0:
  return NULL;
}

static PyMethodDef LSystem_methods[] = {
  {"step", (PyCFunction)LSystem_step, METH_NOARGS},
  {}
};

static PyGetSetDef LSystem_getset[] = {
  {"state", (getter)LSystem_get_state, (setter)LSystem_set_state},
  {"production", (getter)LSystem_get_production, (setter)LSystem_set_production},
  {}
};

static PyTypeObject LSystem_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  .tp_name = "_LSystem.LSystem",
  .tp_basicsize = sizeof(LSystemObject),
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = (newfunc)LSystem_new,
  .tp_dealloc = (destructor)LSystem_dealloc,
  .tp_iter = (getiterfunc)LSystem_iter,
  .tp_methods = LSystem_methods,
  .tp_getset = LSystem_getset,
};

static void LSystemIterator_dealloc(LSystemIteratorObject *self){
  Py_DECREF(self->self);
  PyMem_Free(self->s);
  PyObject_Del(self);
}

static PyObject *LSystemIterator_iternext(LSystemIteratorObject *self){
  PyObject *v;
  int i;
  if(self->p - self->self->s >= self->self->ls * self->self->power)
    return NULL;
  v = PyTuple_New(self->self->power);
  if(v == NULL)
    goto fault0;
  for(i = 0; i < self->self->power; i++){
    PyObject *item;
    self->s[i] += self->p[i];
    item = PyFloat_FromDouble(self->s[i]);
    if(item == NULL)
      goto fault1;
    if(PyTuple_SetItem(v, i, item) != 0)
      goto fault2;
    continue;

  fault2:
    Py_DECREF(item);
    goto fault1;
  }
  self->p += self->self->power;
  return v;

 fault1:
  Py_DECREF(v);
 fault0:
  return NULL;
}

static PyTypeObject LSystemIterator_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  .tp_name = "_LSystem.LSystemIterator",
  .tp_basicsize = sizeof(LSystemIteratorObject),
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_dealloc = (destructor)LSystemIterator_dealloc,
  .tp_iter = PyObject_SelfIter,
  .tp_iternext = (iternextfunc)LSystemIterator_iternext,
};

static void LSystemVIterator_dealloc(LSystemVIteratorObject *self){
  Py_DECREF(self->self);
  PyObject_Del(self);
}

static PyObject *LSystemVIterator_iternext(LSystemVIteratorObject *self){
  PyObject *v;
  int i;
  if(self->n == 0)
    return NULL;
  v = PyTuple_New(self->self->power);
  if(v == NULL)
    goto fault0;
  for(i = 0; i < self->self->power; i++){
    PyObject *item;
    item = PyFloat_FromDouble(self->p[i]);
    if(item == NULL)
      goto fault1;
    if(PyTuple_SetItem(v, i, item) != 0)
      goto fault2;
    continue;

  fault2:
    Py_DECREF(item);
    goto fault1;
  }
  self->n--;
  self->p += self->self->power;
  return v;

 fault1:
  Py_DECREF(v);
 fault0:
  return NULL;
}

static PyTypeObject LSystemVIterator_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  .tp_name = "_LSystem.LSystemVIterator",
  .tp_basicsize = sizeof(LSystemVIteratorObject),
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_dealloc = (destructor)LSystemVIterator_dealloc,
  .tp_iter = PyObject_SelfIter,
  .tp_iternext = (iternextfunc)LSystemVIterator_iternext,
};

static PyMethodDef _LSystem_methods[] = {
  {}
};

PyMODINIT_FUNC init_LSystem(void){
  PyObject *_LSystem;
  if(PyType_Ready(&LSystemIterator_Type) == -1)
    goto fault0;
  if(PyType_Ready(&LSystemVIterator_Type) == -1)
    goto fault0;
  if(PyType_Ready(&LSystem_Type) == -1)
    goto fault0;
  _LSystem = Py_InitModule("_LSystem", _LSystem_methods);
  if(_LSystem == NULL)
    goto fault0;
  Py_INCREF(&LSystem_Type);
  PyModule_AddObject(_LSystem, "LSystem", (PyObject *)&LSystem_Type);
  PyModule_AddStringConstant(_LSystem, "__version__", VERSION);
  PyModule_AddStringConstant(_LSystem, "__release__", "$Id: _LSystem.c 6 2005-07-01 18:53:15Z const $");
  PyModule_AddStringConstant(_LSystem, "__author__", AUTHOR);
  return;

 fault0:
  return;
}
