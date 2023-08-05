#include <Python.h>

typedef struct {
	PyObject_HEAD
	double v[4];
} QuaternionObject;

static PyTypeObject Quaternion_Type;

static QuaternionObject *Quaternion(PyTypeObject *type, double *v){
	QuaternionObject *new;
	unsigned i;
	new = (QuaternionObject *)type->tp_alloc(&Quaternion_Type, 0);
	if(new != 0)
		for(i = 0; i < 4; i++)
			new->v[i] = v[i];
	return new;
}

static QuaternionObject *Quaternion_new(PyTypeObject *type, PyObject *args){
	PyObject *iter;
	unsigned i;
	double v[4];
	if(!PyType_IsSubtype(type, &Quaternion_Type))
		return NULL;
	iter = PyObject_GetIter(args);
	if(iter == NULL)
		return NULL;
	for(i = 0; i < 4; i++){
		PyObject *item = PyIter_Next(iter);
		if(item == NULL){
			if(PyErr_Occurred()){
				Py_DECREF(iter);
				return NULL;
			}else
				break;
		}
		PyObject *val = PyNumber_Float(item);
		Py_DECREF(item);
		if(val == NULL){
			Py_DECREF(iter);
			return NULL;
		}
		v[i] = PyFloat_AsDouble(val);
		Py_DECREF(val);
	}
	Py_DECREF(iter);
	for(; i < 4; v[i++] = 0.0);
	return Quaternion(type, v);
}

static QuaternionObject *Quaternion_add(QuaternionObject *x,
					QuaternionObject *y){
	double v[4];
	unsigned i;
	for(i = 0; i < 4; i++)
		v[i] = x->v[i] + y->v[i];
	return Quaternion(x->ob_type, v);
}

static QuaternionObject *Quaternion_multiply(QuaternionObject *x,
					     QuaternionObject *y){
	double v[4];
	v[0] = (x->v[0] * y->v[0] - x->v[1] * y->v[1] -
		x->v[2] * y->v[2] - x->v[3] * y->v[3]);
	v[1] = (x->v[0] * y->v[1] + x->v[1] * y->v[0] +
		x->v[2] * y->v[3] - x->v[3] * y->v[2]);
	v[2] = (x->v[0] * y->v[2] - x->v[1] * y->v[3] +
		x->v[2] * y->v[0] + x->v[3] * y->v[1]);
	v[3] = (x->v[0] * y->v[3] + x->v[1] * y->v[2] -
		x->v[2] * y->v[1] + x->v[3] * y->v[0]);
	return Quaternion(x->ob_type, v);
}

static double Quaternion_sqr(double *v){
	double X;
	unsigned i;
	for(i = 0, X = 0.0; i < 4; i++)
		X += v[i] * v[i];
	return X;
}

static QuaternionObject *Quaternion_divide(QuaternionObject *x,
					   QuaternionObject *y){
	double v[4], Y;
	Y = Quaternion_sqr(y->v);
	if(Y == 0.0){
		PyErr_SetNone(PyExc_ZeroDivisionError);
		return NULL;
	}
	v[0] = (x->v[0] * y->v[0] + x->v[1] * y->v[1] +
		x->v[2] * y->v[2] + x->v[3] * y->v[3]) / Y;
	v[1] = (-x->v[0] * y->v[1] + x->v[1] * y->v[0] -
		x->v[2] * y->v[3] + x->v[3] * y->v[2]) / Y;
	v[2] = (-x->v[0] * y->v[2] + x->v[1] * y->v[3] +
		x->v[2] * y->v[0] - x->v[3] * y->v[1]) / Y;
	v[3] = (-x->v[0] * y->v[3] - x->v[1] * y->v[2] +
		x->v[2] * y->v[1] + x->v[3] * y->v[0]) / Y;
	return Quaternion(x->ob_type, v);
}

static PyObject *Quaternion_absolute(QuaternionObject *self){
	return PyFloat_FromDouble(sqrt(Quaternion_sqr(self->v)));
}

static QuaternionObject *Quaternion_and(QuaternionObject *x,
					QuaternionObject *y){
	double v[4];
	unsigned i;
	for(i = 0; i < 4; i++)
		v[i] = x->v[i] < y->v[i] ? x->v[i] : y->v[i];
	return Quaternion(x->ob_type, v);
}

static QuaternionObject *Quaternion_or(QuaternionObject *x,
				       QuaternionObject *y){
	double v[4];
	unsigned i;
	for(i = 0; i < 4; i++)
		v[i] = x->v[i] > y->v[i] ? x->v[i] : y->v[i];
	return Quaternion(x->ob_type, v);
}

static int Quaternion_coerce(PyObject **x, PyObject **y){
	PyObject *o;
	double v[4] = {0.0, 0.0, 0.0, 0.0};
	o = PyNumber_Float(*y);
	if(o == NULL)
		return 1;
	v[0] = PyFloat_AsDouble(o);
	Py_DECREF(o);
	if(v[0] == -1.0 && PyErr_Occurred())
		return -1;
	*y = (PyObject *)Quaternion((*x)->ob_type, v);
	Py_INCREF(*x);
	return 0;
}

static PyObject *Quaternion_item(QuaternionObject *self, int i){
	if(i < 0 || i > 3){
		PyErr_SetNone(PyExc_IndexError);
		return NULL;
	}
	return PyFloat_FromDouble(self->v[i]);
}

static PyObject *Quaternion_repr(QuaternionObject *self){
	char buf[80];
	PyOS_snprintf(buf, sizeof(buf) - 1, "(%g, (%g, %g, %g))",
		      self->v[0], self->v[1], self->v[2], self->v[3]);
	return PyString_FromString(buf);
}

static char Quaternion_rotate_doc[] =
	"Quaternion.rotate(t, x, y, z) -> q\n"
	"\n"
	"Rotation of t radians around (x, y, z) as quaternion.";

static QuaternionObject *Quaternion_rotate(PyTypeObject *type, PyObject *args){
	QuaternionObject *new;
	double v;
	unsigned i;
	new = Quaternion_new(type, args);
	if(new == NULL)
		return NULL;
	for(i = 1; i < 4; i++)
		v += new->v[i] * new->v[i];
	new->v[0] *= 0.5;
	v = sin(new->v[0]) / sqrt(v);
	new->v[0] = cos(new->v[0]);
	for(i = 1; i < 4; i++)
		new->v[i] *= v;
	return new;
}

static PyMethodDef Quaternion_methods[] = {
	{"rotate", (PyCFunction)Quaternion_rotate, METH_VARARGS | METH_CLASS,
	 Quaternion_rotate_doc},
	{NULL}
};

static PyNumberMethods Quaternion_as_number = {
	.nb_add = (binaryfunc)Quaternion_add,
	.nb_multiply = (binaryfunc)Quaternion_multiply,
	.nb_divide = (binaryfunc)Quaternion_divide,
	.nb_absolute = (unaryfunc)Quaternion_absolute,
	.nb_and = (binaryfunc)Quaternion_and,
	.nb_or = (binaryfunc)Quaternion_or,
	.nb_coerce = (coercion)Quaternion_coerce,
};

static PySequenceMethods Quaternion_as_sequence = {
	.sq_item = (intargfunc)Quaternion_item,
};

static PyTypeObject Quaternion_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	.tp_name = "Quaternion.Quaternion",
	.tp_basicsize = sizeof(QuaternionObject),
	.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
	.tp_new = (newfunc)Quaternion_new,
	.tp_methods = Quaternion_methods,
	.tp_as_number = &Quaternion_as_number,
	.tp_as_sequence = &Quaternion_as_sequence,
	.tp_repr = (reprfunc)Quaternion_repr,
};

static PyMethodDef module_methods[] = {
	{NULL}
};

PyMODINIT_FUNC initQuaternion(void){
	PyObject *module;
	if(PyType_Ready(&Quaternion_Type))
		return;
	module = Py_InitModule("Quaternion", module_methods);
	if(module == NULL)
		return;
	PyModule_AddObject(module, "Quaternion", (PyObject *)&Quaternion_Type);
	PyModule_AddStringConstant(module, "__revision__", "$Id: Quaternion.c 87 2006-03-12 20:00:13Z const $");
}
