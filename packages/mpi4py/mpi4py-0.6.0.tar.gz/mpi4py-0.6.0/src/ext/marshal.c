/* $Id: marshal.c 145 2007-10-24 00:09:54Z dalcinl $ */

#include <Python.h>

#if PY_VERSION_HEX < 0x02050000
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif

#include "marshal.h"

#if PY_VERSION_HEX < 0x02040000
#define Py_MARSHAL_VERSION 0
#define PyMarshal_WriteObjectToString(obj, version) \
        PyMarshal_WriteObjectToString((obj))
#endif

static PyObject*
marshal_dump(PyObject* self, PyObject* args)
{
  PyObject *msh;
  PyObject *obj;
  PyObject *buf = NULL;
  PyObject *proto = NULL;
  PyObject *res = NULL;

  int version = Py_MARSHAL_VERSION;

  if (!PyArg_ParseTuple(args, "OO|O:dump", &msh, &obj, &buf))
    return NULL;

  proto = PyObject_GetAttrString(msh, "PROTOCOL");

  if (proto == NULL) {
    PyErr_Clear();
  }
  else if (proto == Py_None) {
    Py_DECREF(proto);
  }
  else if (PyInt_Check(proto)) {
    version = (int) PyInt_AS_LONG(proto);
    if (version < 0 || version > Py_MARSHAL_VERSION)
      version = Py_MARSHAL_VERSION;
  }
  else {
    Py_DECREF(proto);
    PyErr_SetString(PyExc_TypeError,
		    "attribute 'PROTOCOL' "
		    "must be None or integer");
    return NULL;
  }

  res = PyMarshal_WriteObjectToString(obj, version);
  if (res == NULL) return NULL;

  if (buf != NULL && buf != Py_None) {
    void *bufptr=NULL, *str=NULL;
    Py_ssize_t buflen=0, len=0;
    str = (void*) PyString_AS_STRING(res);
    len = PyString_GET_SIZE(res);
    if (PyObject_AsWriteBuffer(buf, &bufptr, &buflen) < 0)
      goto fail;
    if (buflen < len) {
      PyErr_SetString(PyExc_ValueError,
		      "buffer to short to hold marshaled object");
      goto fail;
    }
    memcpy(bufptr, str, len);
    Py_DECREF(res); res = NULL;
#if PY_VERSION_HEX < 0x02050000
    res = Py_BuildValue("i", len);
#else
    res = Py_BuildValue("n", len);
#endif
  }

  return res;

 fail:

  Py_XDECREF(res);
  return NULL;

}

static PyObject*
marshal_load(PyObject* self, PyObject* args)
{
  PyObject *msh;
  PyObject *obj;
  char *str = NULL;
  Py_ssize_t len = 0;

  if (!PyArg_ParseTuple(args, "OO:load", &msh, &obj))
    return NULL;

  if (PyString_Check(obj)) {
    str = PyString_AS_STRING(obj);
    len = PyString_GET_SIZE(obj);
  }
  else {
    void *bufptr = NULL;
    if (PyObject_AsReadBuffer(obj, (const void**)&bufptr, &len) < 0)
      return NULL;
    str = (char*) bufptr;
  }

  return PyMarshal_ReadObjectFromString(str, len);

}

static struct PyMethodDef marshal_methods[] =
{
  {"dump", marshal_dump, METH_VARARGS,
   PyDoc_STR("dump(cls, object[, buffer]) -> string or None")},
  {"load", marshal_load, METH_VARARGS,
   PyDoc_STR("load(cls, string|buffer) -> object")},
  {NULL, NULL} /* Sentinel */
};

#define PyInit__marshal init_marshal

PyMODINIT_FUNC
init_marshal(void)
{
  PyObject* m;

  m = Py_InitModule("_marshal", marshal_methods);
  if (m == NULL) return;

  PyModule_AddIntConstant(m, "VERSION", Py_MARSHAL_VERSION);
}
