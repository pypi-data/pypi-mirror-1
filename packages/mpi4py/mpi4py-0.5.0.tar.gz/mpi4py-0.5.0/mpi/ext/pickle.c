/* $Id: pickle.c 66 2007-07-26 22:13:14Z dalcinl $ */ 

#include <Python.h>

static PyObject* Pickle_dump = NULL;
static PyObject* Pickle_load = NULL;
static PyObject* Pickle_PROT = NULL;

#if PY_VERSION_HEX < 0x03000000


#include "cStringIO.h"

#if PY_VERSION_HEX < 0x02050000
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif

static PyObject* 
pickle_dump(PyObject* self, PyObject* args) 
{
  PyObject *pkl;
  PyObject *obj;
  PyObject *file = NULL;
  PyObject *strio = NULL;
  PyObject *proto = NULL;
  PyObject *result = NULL;

  if (!PyArg_ParseTuple(args, "OO|O:dump", &pkl, &obj, &file)) 
    return NULL;

  /* protocol */
  proto = PyObject_GetAttrString(pkl, "PROTOCOL");
  
  if (proto == NULL) {
    PyErr_Clear();
    Py_INCREF(Pickle_PROT);
    proto = Pickle_PROT;
  }
  else if (proto == Py_None) {
    Py_DECREF(proto);
    Py_INCREF(Pickle_PROT);
    proto = Pickle_PROT;
  }
  else if (!PyInt_Check(proto)) {
    PyErr_SetString(PyExc_TypeError,
		    "attribute 'PROTOCOL' "
		    "must be None or integer");
    goto fail;
  }
  
  /* output cStringIO */
  if (file == NULL || file == Py_None ||
      !PycStringIO_OutputCheck(file)) {
    strio = PycStringIO->NewOutput(128);
    if (strio == NULL) goto fail;
  }
  else {
    Py_INCREF(file);
    strio = file;
  }

  /* pikle input object */
  result = PyObject_CallFunctionObjArgs(Pickle_dump, obj, strio, proto, NULL);
  if (result == NULL) goto fail;
  Py_DECREF(result); result = NULL;
  
  /* output pickled stream */
  if (file == NULL || file == Py_None) {
#if PY_VERSION_HEX < 0x03000000
    result = PycStringIO->cgetvalue(strio);
#else /* py3k-struni branch */
    PyObject *tmpstr = PycStringIO->cgetvalue(strio);
    if (tmpstr != NULL) {
      result = PyBytes_FromStringAndSize(PyString_AS_STRING(tmpstr), 
					 PyString_GET_SIZE(tmpstr));
    }
    Py_XDECREF(tmpstr);
#endif
  }
  else if (file != strio) {
    void *buf;
    Py_ssize_t blen;
    char *str;
    Py_ssize_t len;
    result = PyObject_CallMethod(strio, "reset", NULL);
    if (result == NULL) goto fail;
    Py_DECREF(result); result = NULL;
    len = PycStringIO->cread(strio, &str, -1);
    if (len < 0) goto fail;
    if (PyObject_AsWriteBuffer(file, &buf, &blen) < 0) goto fail;
    if (blen < len) {
      PyErr_SetString(PyExc_ValueError,
		      "buffer to short to hold pickled object");
      goto fail;
    }
    memcpy(buf, str, len);
#if PY_VERSION_HEX < 0x02050000
    result = Py_BuildValue("i", len);
#else
    result = Py_BuildValue("n", len);
#endif
  }

  Py_DECREF(proto);
  Py_DECREF(strio);
  return result;

 fail:
  Py_XDECREF(proto);
  Py_XDECREF(strio);
  Py_XDECREF(result);
  return NULL;

}

static PyObject* 
pickle_load(PyObject* self, PyObject* args) 
{
  PyObject *pkl;
  PyObject *obj;
  PyObject *file = NULL;
  PyObject *result = NULL;

  if (!PyArg_ParseTuple(args, "OO:load", &pkl, &obj))
    return NULL;
  
  if (PycStringIO_InputCheck(obj)) {
    Py_INCREF(obj);
    file = obj;
  } 
  else {
    PyObject *buf; void *bptr; Py_ssize_t blen;
    if (PyObject_AsReadBuffer(obj, (const void **)&bptr, &blen) != 0)
      return NULL;
    buf = PyBuffer_FromMemory(bptr, blen);
    if (buf == NULL) return NULL;
    file = PycStringIO->NewInput(buf);
    if (file == NULL) { 
      Py_DECREF(buf); return NULL; 
    }
  }
  result = PyObject_CallFunctionObjArgs(Pickle_load, file, NULL);
  Py_DECREF(file);
  return result;
}

static struct PyMethodDef pickle_methods[] = 
{
  {"dump", pickle_dump, METH_VARARGS,
   PyDoc_STR("dump(cls, object[, buffer]) -> string or None")},
  {"load", pickle_load, METH_VARARGS,
   PyDoc_STR("load(cls, string|buffer) -> object")},
  {NULL, NULL} /* Sentinel */
};

PyMODINIT_FUNC
init_pickle(void) 
{
  PyObject* m = NULL;

  PycString_IMPORT;
  if (PycStringIO == NULL) return;

  m = PyImport_ImportModule("cPickle");
  if (m == NULL) {
    PyErr_Clear();
    m = PyImport_ImportModule("pickle");
  }
  if (m == NULL) return;

  Pickle_dump = PyObject_GetAttrString(m, "dump");
  if (Pickle_dump == NULL) return;
  Pickle_load = PyObject_GetAttrString(m, "load");
  if (Pickle_load == NULL) return;
  Pickle_PROT = PyObject_GetAttrString(m, "HIGHEST_PROTOCOL");
  if (Pickle_PROT == NULL) return;

  Py_DECREF(m);
  
  m = Py_InitModule("_pickle", pickle_methods);
  if (m == NULL) return;

  if (PyModule_AddObject(m, "_load",     Pickle_load) < 0) return;
  if (PyModule_AddObject(m, "_dump",     Pickle_dump) < 0) return;
  if (PyModule_AddObject(m, "HIGH_PROT", Pickle_PROT) < 0) return;
}


#else /* py3k-struni branch */


static PyObject* 
pickle_dump(PyObject* self, PyObject* args) 
{
  PyObject *pkl;
  PyObject *obj;
  PyObject *proto = NULL;
  PyObject *file = NULL;
  PyObject *result = NULL;

  if (!PyArg_ParseTuple(args, "OO|O:dump", &pkl, &obj, &file))
    return NULL;

  if (file != NULL) {
    PyErr_SetString(PyExc_NotImplementedError,
		    "last argument not suported in py3k");
    goto fail;
  }

  /* protocol */
  proto = PyObject_GetAttrString(pkl, "PROTOCOL");
  if (proto == NULL) {
    PyErr_Clear();
    proto = Pickle_PROT;
    Py_INCREF(proto);
  }
  else if (proto == Py_None) {
    Py_DECREF(proto);
    proto = Pickle_PROT;
    Py_INCREF(proto);
  }
  else if (!PyInt_Check(proto)) {
    PyErr_SetString(PyExc_TypeError,
		    "attribute 'PROTOCOL' "
		    "must be None or integer");
    goto fail;
  }

  /* pikle input object */
  result = PyObject_CallFunctionObjArgs(Pickle_dump, obj, proto, NULL);
  if (result == NULL) goto fail;

  Py_DECREF(proto);
  return result;

 fail:
  Py_XDECREF(proto);
  Py_XDECREF(result);
  return NULL;
}

static PyObject* 
pickle_load(PyObject* self, PyObject* args) 
{
  PyObject *pkl;
  PyObject *obj;
  PyObject *result = NULL;

  if (!PyArg_ParseTuple(args, "OO:load", &pkl, &obj))
    return NULL;
  
  result = PyObject_CallFunctionObjArgs(Pickle_load, obj, NULL);
  return result;
}

static struct PyMethodDef pickle_methods[] = 
{
  {"dump", pickle_dump, METH_VARARGS,
   PyDoc_STR("dump(cls, object[, buffer]) -> string or None")},
  {"load", pickle_load, METH_VARARGS,
   PyDoc_STR("load(cls, string|buffer) -> object")},
  {NULL, NULL} /* Sentinel */
};

PyMODINIT_FUNC
init_pickle(void) 
{
  PyObject* m;

  m = PyImport_ImportModule("pickle");
  if (m == NULL) return;
  Pickle_dump = PyObject_GetAttrString(m, "dumps");
  if (Pickle_dump == NULL) return;
  Pickle_load = PyObject_GetAttrString(m, "loads");
  if (Pickle_load == NULL) return;
  Pickle_PROT = PyObject_GetAttrString(m, "HIGHEST_PROTOCOL");
  if (Pickle_PROT == NULL) return;
  Py_DECREF(m);
  
  m = Py_InitModule("_pickle", pickle_methods);
  if (m == NULL) return;

  if (PyModule_AddObject(m, "_load",     Pickle_load) < 0) return;
  if (PyModule_AddObject(m, "_dump",     Pickle_dump) < 0) return;
  if (PyModule_AddObject(m, "HIGH_PROT", Pickle_PROT) < 0) return;
}


#endif
