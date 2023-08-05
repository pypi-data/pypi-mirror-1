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
		if(item == NULL)
			if(PyErr_Occurred()){
				Py_DECREF(iter);
				return NULL;
			}else
				break;
		if(i == 0 && PyComplex_Check(item)){
			Py_complex val = PyComplex_AsCComplex(item);
			Py_DECREF(item);
			v[0] = val.real;
			v[1] = val.imag;
			i++;
		}else{
			PyObject *val = PyNumber_Float(item);
			Py_DECREF(item);
			if(val == NULL){
				Py_DECREF(iter);
				return NULL;
			}
			v[i] = PyFloat_AsDouble(val);
			Py_DECREF(val);
		}
	}
	Py_DECREF(iter);
	for(; i < 4; i++)
		v[i] = 0.0;
	return Quaternion(type, v);
}

static PyObject *Quaternion_call(QuaternionObject *self){
	return Py_BuildValue("(dddd)", self->v[0], self->v[1],
			     self->v[2], self->v[3]);
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

static QuaternionObject *Quaternion_divide(QuaternionObject *y,
					   QuaternionObject *x){
	double v[4], X;
	unsigned i;
	for(i = 0, X = 0.0; i < 4; i++)
		X += x->v[i] * x->v[i];
	if(X == 0.0){
		PyErr_SetNone(PyExc_ZeroDivisionError);
		return NULL;
	}
	v[0] = (x->v[0] * y->v[0] + x->v[1] * y->v[1] +
		x->v[2] * y->v[2] + x->v[3] * y->v[3]) / X;
	v[1] = (x->v[0] * y->v[1] - x->v[1] * y->v[0] -
		x->v[2] * y->v[3] + x->v[3] * y->v[2]) / X;
	v[2] = (x->v[0] * y->v[2] + x->v[1] * y->v[3] -
		x->v[2] * y->v[0] - x->v[3] * y->v[1]) / X;
	v[3] = (x->v[0] * y->v[3] - x->v[1] * y->v[2] +
		x->v[2] * y->v[1] - x->v[3] * y->v[0]) / X;
	return Quaternion(y->ob_type, v);
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

static PyObject *Quaternion_item(QuaternionObject *self, int i){
	if(i < 0 || i > 3){
		PyErr_SetNone(PyExc_IndexError);
		return NULL;
	}
	return PyFloat_FromDouble(self->v[i]);
}

static PyNumberMethods Quaternion_as_number = {
	.nb_add = (binaryfunc)Quaternion_add,
	.nb_multiply = (binaryfunc)Quaternion_multiply,
	.nb_divide = (binaryfunc)Quaternion_divide,
	.nb_and = (binaryfunc)Quaternion_and,
	.nb_or = (binaryfunc)Quaternion_or,
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
	.tp_call = (ternaryfunc)Quaternion_call,
	.tp_as_number = &Quaternion_as_number,
	.tp_as_sequence = &Quaternion_as_sequence,
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
	PyModule_AddStringConstant(module, "__revision__", "$Id: Quaternion.c 71 2005-12-04 20:08:21Z const $");
}
