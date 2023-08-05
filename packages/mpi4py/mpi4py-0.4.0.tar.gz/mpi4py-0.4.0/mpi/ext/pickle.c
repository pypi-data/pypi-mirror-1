/* $Id: pickle.c 32 2007-06-01 17:59:00Z dalcinl $ */ 

#include <Python.h>
#include "cStringIO.h"

#if PY_VERSION_HEX < 0x02050000
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif

static PyObject* cPickle_dump  = NULL;
static PyObject* cPickle_load  = NULL;
static PyObject* cPickle_HIGH_PROT = NULL;

static PyObject* 
pickle_dump(PyObject* self, PyObject* args) 
{
  PyObject *pkl;
  PyObject *obj;
  PyObject *file = NULL;
  PyObject *strio = NULL;
  PyObject *proto = NULL;
  PyObject *res = NULL;

  if (!PyArg_ParseTuple(args, "OO|O:dump", &pkl, &obj, &file)) 
    return NULL;

  /* protocol */
  proto = PyObject_GetAttrString(pkl, "PROTOCOL");
  
  if (proto == NULL) {
    PyErr_Clear();
    Py_INCREF(cPickle_HIGH_PROT);
    proto = cPickle_HIGH_PROT;
  }
  else if (proto == Py_None) {
    Py_DECREF(proto);
    Py_INCREF(cPickle_HIGH_PROT);
    proto = cPickle_HIGH_PROT;
  }
  else if (!PyInt_Check(proto)) {
    PyErr_SetString(PyExc_TypeError,
		    "attribute 'PROTOCOL' "
		    "must be None or integer");
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
  res = PyObject_CallFunctionObjArgs(cPickle_dump, obj, strio, proto, NULL);
  if (res == NULL) goto fail;
  Py_DECREF(res); res = NULL;
  
  /* output pickled stream */
  if (file == NULL || file == Py_None) {
    res = PycStringIO->cgetvalue(strio);
  }
  else if (file != strio) {
    void *buf;
    Py_ssize_t blen;
    char *str;
    Py_ssize_t len;
    res = PyObject_CallMethod(strio, "reset", NULL);
    if (res == NULL) goto fail;
    Py_DECREF(res); res = NULL;
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
    res = Py_BuildValue("i", len);
#else
    res = Py_BuildValue("n", len);
#endif
  }

  Py_DECREF(proto);
  Py_DECREF(strio);
  return res;

 fail:
  Py_XDECREF(proto);
  Py_XDECREF(strio);
  Py_XDECREF(res);
  return NULL;

}

static PyObject* 
pickle_load(PyObject* self, PyObject* args) 
{
  PyObject *pkl;
  PyObject *obj;
  PyObject *file = NULL;
  PyObject *res = NULL;

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
    if (file == NULL) return NULL;
  }
  res = PyObject_CallFunctionObjArgs(cPickle_load, file, NULL);
  Py_DECREF(file);
  return res;
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

  PycString_IMPORT;
  if (PycStringIO == NULL) return;

  m = PyImport_ImportModule("cPickle");
  if (m == NULL) return;

  cPickle_load = PyObject_GetAttrString(m, "load");
  if (cPickle_load == NULL) return;
  cPickle_dump = PyObject_GetAttrString(m, "dump");
  if (cPickle_dump == NULL) return;
  cPickle_HIGH_PROT = PyObject_GetAttrString(m, "HIGHEST_PROTOCOL");
  if (cPickle_HIGH_PROT == NULL) return;

  Py_DECREF(m);
  
  m = Py_InitModule("_pickle", pickle_methods);
  if (m == NULL) return;

  if (PyModule_AddObject(m, "_load",  cPickle_load)  < 0) return;
  if (PyModule_AddObject(m, "_dump",  cPickle_dump)  < 0) return;
  if (PyModule_AddObject(m, "HIGH_PROT", cPickle_HIGH_PROT) < 0) return;
}
