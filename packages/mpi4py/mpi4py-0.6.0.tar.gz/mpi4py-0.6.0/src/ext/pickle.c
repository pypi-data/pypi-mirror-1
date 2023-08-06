/* $Id: pickle.c 150 2007-11-19 21:55:42Z dalcinl $ */

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
  PyObject *retv = NULL;

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
  if (file == NULL || 
      file == Py_None || 
      !PycStringIO_OutputCheck(file)) {
    strio = PycStringIO->NewOutput(128);
    if (strio == NULL) goto fail;
  }
  else {
    Py_INCREF(file);
    strio = file;
  }

  /* pikle input object */
  retv = PyObject_CallFunctionObjArgs(Pickle_dump, obj, strio, proto, NULL);
  if (retv == NULL) goto fail; Py_DECREF(retv); retv = NULL;

  /* output pickled stream */
  if (file == NULL || file == Py_None) {
    char *sptr; Py_ssize_t slen;
    void *bptr; Py_ssize_t blen;
    retv = PyObject_CallMethod(strio, "reset", NULL);
    if (retv == NULL) goto fail; Py_DECREF(retv); retv = NULL;
    slen = PycStringIO->cread(strio, &sptr, -1);
    if (slen < 0) goto fail;
    result = PyBuffer_New((Py_ssize_t)slen);
    if (result == NULL) goto fail;
    if (PyObject_AsWriteBuffer(result, &bptr, &blen) < 0) goto fail;
    memcpy(bptr, sptr, slen);
  }
  else if (file != strio) {
    char *sptr; Py_ssize_t slen;
    void *bptr; Py_ssize_t blen;
    retv = PyObject_CallMethod(strio, "reset", NULL);
    if (retv == NULL) goto fail; Py_DECREF(retv); retv = NULL;
    slen = PycStringIO->cread(strio, &sptr, -1);
    if (slen < 0) goto fail;
    if (PyObject_AsWriteBuffer(file, &bptr, &blen) < 0) goto fail;
    if (blen < slen) {
      PyErr_SetString(PyExc_ValueError,
		      "buffer to short to hold pickled object");
      goto fail;
    }
    memcpy(bptr, sptr, slen);
#if PY_VERSION_HEX < 0x02050000
    result = Py_BuildValue("i", slen);
#else
    result = Py_BuildValue("n", slen);
#endif
  }
  else {
    result = Py_None; Py_INCREF(result);
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
  PyObject *obuf = NULL;
  PyObject *strio = NULL;
  PyObject *result = NULL;

  if (!PyArg_ParseTuple(args, "OO:load", &pkl, &obj))
    return NULL;

  if (PycStringIO_InputCheck(obj)) {
    Py_INCREF(obj); strio = obj;
  } 
  else {
    void *bptr; Py_ssize_t blen;
    int iret = PyObject_AsReadBuffer(obj, (const void **)&bptr, &blen);
    if ( iret < 0) goto fail;
    obuf = PyBuffer_FromMemory(bptr, blen);
    if (obuf == NULL)  goto fail;
    strio = PycStringIO->NewInput(obuf);
    if (strio == NULL) goto fail;
  }
  result = PyObject_CallFunctionObjArgs(Pickle_load, strio, NULL);
  if (result == NULL) goto fail;
  Py_XDECREF(obuf);
  Py_XDECREF(strio);
  return result;
 fail:
  Py_XDECREF(obuf);
  Py_XDECREF(strio);
  Py_XDECREF(result);
  return NULL;
}

static struct PyMethodDef pickle_methods[] =
{
  {"dump", pickle_dump, METH_VARARGS,
   PyDoc_STR("dump(cls, object[, buffer]) -> string or None")},
  {"load", pickle_load, METH_VARARGS,
   PyDoc_STR("load(cls, string|buffer) -> object")},
  {NULL, NULL} /* Sentinel */
};

#define PyInit__pickle init_pickle

PyMODINIT_FUNC
PyInit__pickle(void)
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


#else /* py3k branch */


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
		    "last argument not yet suported in py3k");
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

#define PyInit__pickle init_pickle

PyMODINIT_FUNC
PyInit__pickle(void)
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
