#include <Python.h>

static PyObject *
set_co_code(PyObject *self, PyObject *args)
{
  PyObject* c; // PyCodeObject
  PyObject* s; // PyString

  if (!PyArg_ParseTuple(args, "OO", &c, &s))
	return NULL;
  PyCodeObject* code = (PyCodeObject*) c;
  Py_INCREF(s);
  code->co_code = s;
  Py_RETURN_NONE;
}

static PyObject *
get_value(PyObject *self, PyObject *args)
{
  PyObject* c; // PyCodeObject

  if (!PyArg_ParseTuple(args, "O", &c))
	return NULL;
  PyCodeObject* code = (PyCodeObject*) c;
  Py_INCREF(c);
  return Py_BuildValue(
	"[iiiiOOOOOOOOiO]",
	code->co_argcount,
	code->co_nlocals,
	code->co_stacksize,
	code->co_flags,
	code->co_code,
	code->co_consts,
	code->co_names,
	code->co_varnames,
	code->co_freevars,
	code->co_cellvars,
	code->co_filename,
	code->co_name,
	code->co_firstlineno,
	code->co_lnotab
  );
}

static PyObject *
set_value(PyObject *self, PyObject *args)
{
  PyCodeObject* code; // PyCodeObject
  PyObject* value;

  if (!PyArg_ParseTuple(args, "OO", &code, &value)) return NULL;
  if (!PyArg_ParseTuple(PyList_AsTuple(value), "iiiiOOOOOOOOiO",
	&code->co_argcount,
	&code->co_nlocals,
	&code->co_stacksize,
	&code->co_flags,
	&code->co_code,
	&code->co_consts,
	&code->co_names,
	&code->co_varnames,
	&code->co_freevars,
	&code->co_cellvars,
	&code->co_filename,
	&code->co_name,
	&code->co_firstlineno,
	&code->co_lnotab))
	return NULL;

  Py_INCREF(code);
  Py_INCREF(code->co_code);
  Py_INCREF(code->co_consts);
  Py_INCREF(code->co_names);
  Py_INCREF(code->co_varnames);
  Py_INCREF(code->co_freevars);
  Py_INCREF(code->co_cellvars);
  Py_INCREF(code->co_filename);
  Py_INCREF(code->co_name);
  Py_INCREF(code->co_lnotab);

  Py_RETURN_NONE;
}

static PyMethodDef Methods[] = {
  {"set_co_code", set_co_code, METH_VARARGS, "overwrite co_code"},
  {"get_value", get_value, METH_VARARGS, "get value of PyCodeObject"},
  {"set_value", set_value, METH_VARARGS, "set value to PyCodeObject"},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initcodehack_bin(void)
{
  (void) Py_InitModule("codehack_bin", Methods);
}
