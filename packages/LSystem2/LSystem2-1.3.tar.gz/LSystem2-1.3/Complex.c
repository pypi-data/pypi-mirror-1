#include <Python.h>
#include <structmember.h>

typedef struct {
	PyObject_HEAD
	unsigned long power;
	double *v;
} ComplexObject;

static PyTypeObject Complex_Type;

static ComplexObject *Complex_New(PyTypeObject *type,
				  unsigned long power, double *v){
	ComplexObject *new;

	new = (ComplexObject *)type->tp_alloc(&Complex_Type, 0);
	if(new == NULL)
		goto fail_1;
	new->power = power;
	new->v = v;
	return new;

 fail_1:
	PyMem_Del(v);
	return NULL;
}

static ComplexObject *Complex_new(PyTypeObject *type, PyObject *args){
	PyObject *Power, *num;
	PyObject *V, *iter, *item;
	unsigned long power, i;
	double *v;

	if(!PyType_IsSubtype(type, &Complex_Type))
		goto fail_1;

	Power = PySequence_GetItem(args, 0);
	if(Power == NULL)
		goto fail_1;
	num = PyNumber_Long(Power);
	Py_DECREF(Power);
	if(num == NULL)
		goto fail_1;
	power = PyLong_AsUnsignedLong(num);
	Py_DECREF(num);
	if(PyErr_Occurred() || num == 0)
		goto fail_1;

	v = PyMem_New(double, power);
	if(v == NULL)
		goto fail_1;

	V = PySequence_GetItem(args, 1);
	if(V == NULL)
		goto fail_2;
	iter = PyObject_GetIter(V);
	Py_DECREF(V);
	if(iter == NULL)
		goto fail_2;
	for(i = 0; i < power && (item = PyIter_Next(iter)); i++){
		num = PyNumber_Float(item);
		Py_DECREF(item);
		if(num == NULL)
			break;
		v[i] = PyFloat_AsDouble(num);
		Py_DECREF(num);
		if(PyErr_Occurred())
			break;
	}
	Py_DECREF(iter);
	if(PyErr_Occurred())
		goto fail_2;
	while(i < power)
		v[i++] = 0;
	return Complex_New(type, power, v);

 fail_2:
	PyMem_Del(v);
 fail_1:
	return NULL;
}

static void Complex_dealloc(ComplexObject *self){
	PyMem_Del(self->v);
	self->ob_type->tp_free(self);
}

static PyObject *Complex_tuple(ComplexObject *self){
	PyObject *v;
	int i;

	v = PyTuple_New(self->power);
	if(v == NULL)
		goto fail_1;
	for(i = 0; i < self->power; i++){
		PyObject *num;

		num = PyFloat_FromDouble(self->v[i]);
		if(num == NULL)
			goto fail_2;
		if(PyTuple_SetItem(v, i, num)){
			Py_DECREF(num);
			goto fail_2;
		}
	}
	return v;

 fail_2:
	Py_DECREF(v);
 fail_1:
	return NULL;
}

static ComplexObject *Complex_copy(ComplexObject *self){
	double *v;
	unsigned long i;

	v = PyMem_New(double, self->power);
	if(v == NULL)
		goto fail_1;
	for(i = 0; i < self->power; i++)
		v[i] = self->v[i];
	return Complex_New(self->ob_type, self->power, v);

 fail_1:
	return NULL;
}

static ComplexObject *Complex_add(ComplexObject *x, ComplexObject *y){
	double *v;
	unsigned long i;

	if(x->power != y->power)
		goto fail_1;
	v = PyMem_New(double, x->power);
	if(v == NULL)
		goto fail_1;
	for(i = 0; i < x->power; i++)
		v[i] = x->v[i] + y->v[i];
	return Complex_New(x->ob_type, x->power, v);

 fail_1:
	return NULL;
}

static ComplexObject *Complex_inplace_add(ComplexObject *x, ComplexObject *y){
	unsigned long i;

	if(x->power != y->power)
		goto fail_1;
	for(i = 0; i < x->power; i++)
		x->v[i] += y->v[i];
	Py_INCREF(x);
	return x;

 fail_1:
	return NULL;
}

static ComplexObject *Complex_multiply(ComplexObject *x, ComplexObject *y){
	double *v;
	unsigned long i;

	if(x->power != y->power)
		goto fail_1;
	v = PyMem_New(double, x->power);
	if(v == NULL)
		goto fail_1;
	v[0] = x->v[0] * y->v[0];
	for(i = 1; i < x->power; i++){
		v[0] -= x->v[i] * y->v[i];
		v[i] = x->v[0] * y->v[i] + x->v[i] * y->v[0];
	}
	return Complex_New(x->ob_type, x->power, v);

 fail_1:
	return NULL;
}

static ComplexObject *Complex_divide(ComplexObject *x, ComplexObject *y){
	double *v, Y;
	unsigned long i;

	if(x->power != y->power)
		goto fail_1;
	v = PyMem_New(double, x->power);
	if(v == NULL)
		goto fail_1;
	for(Y = 0, i = 0; i < y->power; i++)
		Y += y->v[i] * y->v[i];
	v[0] = x->v[0] * y->v[0];
	for(i = 1; i < x->power; i++){
		v[0] += x->v[i] * y->v[i];
		v[i] = (x->v[i] * y->v[0] - x->v[0] * y->v[i]) / Y;
	}
	v[0] /= Y;
	return Complex_New(x->ob_type, x->power, v);

 fail_1:
	return NULL;
}

static PyMemberDef Complex_members[] = {
	{"power", T_ULONG, offsetof(ComplexObject, power), READONLY},
	{}
};

static PyMethodDef Complex_methods[] = {
	{"tuple", (PyCFunction)Complex_tuple, METH_NOARGS},
	{"copy", (PyCFunction)Complex_copy, METH_NOARGS},
	{}
};

static PyNumberMethods Complex_as_number = {
	.nb_add = (binaryfunc)Complex_add,
	.nb_inplace_add = (binaryfunc)Complex_inplace_add,
	.nb_multiply = (binaryfunc)Complex_multiply,
	.nb_divide = (binaryfunc)Complex_divide,
};

static PyTypeObject Complex_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	.tp_name = "Complex.Complex",
	.tp_basicsize = sizeof(ComplexObject),
	.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
	.tp_new = (newfunc)Complex_new,
	.tp_dealloc = (destructor)Complex_dealloc,
	.tp_members = Complex_members,
	.tp_methods = Complex_methods,
	.tp_as_number = &Complex_as_number,
};

static PyObject *adjust_bounds(PyObject *self, PyObject *args){
	PyObject *bounds;
	ComplexObject *min, *max, *curr;
	unsigned long i;

	bounds = PySequence_GetItem(args, 0);
	if(bounds == NULL)
		goto fail_1;
	min = (ComplexObject *)PySequence_GetItem(bounds, 0);
	if(min == NULL){
		Py_DECREF(bounds);
		goto fail_1;
	}
	max = (ComplexObject *)PySequence_GetItem(bounds, 1);
	if(max == NULL){
		Py_DECREF(bounds);
		goto fail_2;
	}
	if(!(PyObject_IsInstance((PyObject *)min, (PyObject *)&Complex_Type) &&
	     PyObject_IsInstance((PyObject *)max, (PyObject *)&Complex_Type)
	     ))
		goto fail_3;
	Py_DECREF(bounds);
	curr = (ComplexObject *)PySequence_GetItem(args, 1);
	if(curr == NULL)
		goto fail_3;
	if(!PyObject_IsInstance((PyObject *)curr, (PyObject *)&Complex_Type))
		goto fail_4;
	for(i = 0; i < curr->power; i++)
		if(curr->v[i] < min->v[i])
			min->v[i] = curr->v[i];
		else if(curr->v[i] > max->v[i])
			max->v[i] = curr->v[i];
	Py_DECREF(min);
	Py_DECREF(max);
	Py_DECREF(curr);
	Py_INCREF(Py_None);
	return Py_None;

 fail_4:
	Py_DECREF(curr);
 fail_3:
	Py_DECREF(max);
 fail_2:
	Py_DECREF(min);
 fail_1:
	return NULL;
}

static PyMethodDef module_methods[] = {
	{"adjust_bounds", (PyCFunction)adjust_bounds, METH_VARARGS},
	{}
};

PyMODINIT_FUNC initComplex(void){
	PyObject *module;

	if(PyType_Ready(&Complex_Type) == -1)
		goto fail_1;
	module = Py_InitModule("Complex", module_methods);
	if(module == NULL)
		goto fail_1;
	PyModule_AddObject(module, "Complex", (PyObject *)&Complex_Type);
	PyModule_AddStringConstant(module, "__revision__", "$Id: Complex.c 36 2005-10-17 06:25:20Z const $");
	return;

 fail_1:
	return;
}
