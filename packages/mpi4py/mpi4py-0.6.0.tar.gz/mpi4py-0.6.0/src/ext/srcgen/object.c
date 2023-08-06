/* PyMPI<Obj>_Type implementation */

static void
<obj>_inner_dealloc(_Py_MPI_<Obj> *self)
{
#if MPI4PY_ENABLE_LEAK_WARNING
#if !defined(Py_MPISTATUSOBJECT_H)
  if (self && self-><obj> != MPI_<OBJ>_NULL && !self->isref) {
    PyErr_Warn(PyExc_UserWarning,
	       "<Obj>: possible leak of inner MPI_<Obj> handle");
  }
#else
  /* no leak possible for Status  */
#endif
#endif /* MPI4PY_ENABLE_LEAK_WARNING */
  PyObject_Del(self);
}

static PyTypeObject _Py_MPI_<Obj>_Type = {
#if PY_VERSION_HEX < 0x03000000
  PyObject_HEAD_INIT(NULL) 0,
#else
  PyVarObject_HEAD_INIT(&PyType_Type, 0)
#endif
  "_Py_MPI_<Obj>",			/*tp_name*/
  sizeof(_Py_MPI_<Obj>),		/*tp_basicsize*/
  0,					/*tp_itemsize*/
  (destructor)<obj>_inner_dealloc,	/*tp_dealloc*/
  0,
};


#if !defined(Py_MPISTATUSOBJECT_H)
#define PyMPI_<OBJ>_DEFAULT MPI_<OBJ>_NULL
#else
static void status_set_empty(MPI_Status *status)
{
  memset(status, 0, sizeof(MPI_Status));
  status->MPI_SOURCE = MPI_ANY_SOURCE;
  status->MPI_TAG    = MPI_ANY_TAG;
  status->MPI_ERROR  = MPI_SUCCESS;
}
static MPI_Status status_empty(void)
{
  MPI_Status status;
  status_set_empty(&status);
  return status;
}
#define PyMPI_STATUS_DEFAULT status_empty()
#endif

#define <obj>_alloc PyType_GenericAlloc

static void
<obj>_dealloc(PyMPI<Obj>Object *self)
{
  Py_XDECREF(self->ob_mpi);
  Py_TYPE(self)->tp_free(self);
}

static PyObject *
<obj>_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"<obj>", 0};

  if (!PyArg_ParseTupleAndKeywords(args, kwds,
				   "|O:<Obj>", kwlist,
				   &ob)) return NULL;

  if (ob == NULL || ob == Py_None) {
    PyMPI<Obj>Object *self;
    self = (PyMPI<Obj>Object*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->ob_mpi = (PyObject*) PyObject_New(_Py_MPI_<Obj>,
					      &_Py_MPI_<Obj>_Type);
      if (self->ob_mpi == NULL) {
	Py_DECREF(self);
	return NULL;
      }
#if !defined(Py_MPISTATUSOBJECT_H)
      PyMPI<Obj>_AS_<OBJ>(self) = MPI_<OBJ>_NULL;
#else
      status_set_empty(PyMPI<Obj>_AS_<OBJ>_PTR(self));
#endif
    }
    return (PyObject*)self;
  }

#if !defined(Py_MPISTATUSOBJECT_H)
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

#else
#endif
  if (PyMPI<Obj>_Check(ob)) {
    PyMPI<Obj>Object *self;
    self = (PyMPI<Obj>Object*) type->tp_alloc(type, 0);
    if (self != NULL) {
#if !defined(Py_MPISTATUSOBJECT_H)
      self->ob_mpi = ((PyMPI<Obj>Object*)ob)->ob_mpi;
      if (self->ob_mpi == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->ob_mpi);
#else
      self->ob_mpi = (PyObject*) PyObject_New(_Py_MPI_Status,
					      &_Py_MPI_Status_Type);
      if (self->ob_mpi == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIStatus_AS_STATUS(self) = PyMPIStatus_AS_STATUS(ob);
#endif
    }
    return (PyObject*) self;
  }

  PyErr_SetString(PyExc_TypeError,
		  "<Obj>() argument must be a '<Obj>' object");
  return NULL;
}

static int
<obj>_init(PyMPI<Obj>Object *self, PyObject *args, PyObject *kwds)
{
  assert(self->ob_mpi != NULL);
  return 0;
}

static long
<obj>_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'<Obj>' objects are unhashable");
  return -1;
}

static PyObject *
<obj>_richcompare(PyMPI<Obj>Object * o1, PyMPI<Obj>Object * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPI<Obj>_Check((PyObject*)o1) &&
	PyMPI<Obj>_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
#if !defined(Py_MPISTATUSOBJECT_H)
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare '<Obj>' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) ==
      (PyMPI<Obj>_AS_<OBJ>(o1) == PyMPI<Obj>_AS_<OBJ>(o2)))
    res = Py_True;
  else
    res = Py_False;

  Py_INCREF(res);
#else
  PyErr_SetString(PyExc_TypeError,
		  "cannot compare 'Status' objects");
  res = NULL;
#endif
  return res;
}



#if !defined(Py_MPISTATUSOBJECT_H)
static int
<obj>_bool(PyMPI<Obj>Object* ob)
{
  return PyMPI<Obj>_AS_<OBJ>(ob) != MPI_<OBJ>_NULL;
}
static PyNumberMethods <obj>_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
#if PY_VERSION_HEX < 0x03000000
	0, 	 	 	/*nb_divide*/
#endif
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)<obj>_bool,	/*nb_bool*/\
	0,			/*nb_invert*/
	0,			/*nb_lshift*/
	0,			/*nb_rshift*/
	0,			/*nb_and*/
	0,			/*nb_xor*/
	0,			/*nb_or*/
	0,			/*nb_coerce*/
	0,			/*nb_int*/
	0,			/*nb_long*/
	0,			/*nb_float*/
	0,			/*nb_oct*/
	0,			/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
#if PY_VERSION_HEX < 0x03000000
	0,			/*nb_inplace_divide*/
#endif
	0,			/*nb_inplace_remainder*/
	0,			/*nb_inplace_power*/
	0,			/*nb_inplace_lshift*/
	0,			/*nb_inplace_rshift*/
	0,			/*nb_inplace_and*/
	0,			/*nb_inplace_xor*/
	0,			/*nb_inplace_or*/
	0,			/*nb_floor_divide */
	0,			/*nb_true_divide */
	0,			/*nb_inplace_floor_divide */
	0,			/*nb_inplace_true_divide */
};
#define <obj>_as_number   &<obj>_number_methods
#else
#define <obj>_as_number   (PyNumberMethods*)0
#endif
#define <obj>_as_sequence (PySequenceMethods*)0
#define <obj>_as_mapping  (PyMappingMethods*)0


#define <obj>_methods 0
#define <obj>_members 0
#if !defined(Py_MPISTATUSOBJECT_H)
#define <obj>_getset  0
#else
#define LIBMPI_STATUS_GETSETER(ATTRIB) \
static PyObject * \
status_get_##ATTRIB(PyMPIStatusObject *self, void *closure) \
{ \
  return PyInt_FromLong((long)(PyMPIStatus_AS_STATUS(self).MPI_##ATTRIB)); \
} \
static int \
status_set_##ATTRIB(PyMPIStatusObject *self, PyObject *value, void *closure) \
{ \
  if (value == NULL) { \
    PyErr_SetString(PyExc_TypeError, "cannot delete attribute"); \
    return -1; \
  } \
  if (!PyInt_Check(value)) { \
    PyErr_SetString(PyExc_TypeError, "attribute value must be a integer"); \
    return -1; \
  } \
  PyMPIStatus_AS_STATUS(self).MPI_##ATTRIB = (int) PyInt_AS_LONG(value); \
  return 0; \
}
LIBMPI_STATUS_GETSETER(SOURCE)
LIBMPI_STATUS_GETSETER(TAG)
LIBMPI_STATUS_GETSETER(ERROR)
static PyGetSetDef status_getset[] =
{
  {"MPI_SOURCE",
   (getter)status_get_SOURCE, (setter)status_set_SOURCE,
   "message source", NULL},
  {"MPI_TAG",
   (getter)status_get_TAG,    (setter)status_set_TAG,
   "message tag",    NULL},
  {"MPI_ERROR",
   (getter)status_get_ERROR,  (setter)status_set_ERROR,
   "message error",  NULL},
  {NULL}  /* Sentinel */
};
#endif


PyDoc_STRVAR(<obj>_doc, "<Obj> type");

static PyTypeObject PyMPI<Obj>_Type = {
#if PY_VERSION_HEX < 0x03000000
  PyObject_HEAD_INIT(NULL) 0,
#else
  PyVarObject_HEAD_INIT(&PyType_Type, 0)
#endif
  "<Obj>",			        /*tp_name*/
  sizeof(PyMPI<Obj>Object),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)<obj>_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  <obj>_as_number,			/*tp_as_number*/
  <obj>_as_sequence,			/*tp_as_sequence*/
  <obj>_as_mapping,			/*tp_as_mapping*/

  (hashfunc)<obj>_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  <obj>_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)<obj>_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  <obj>_methods,			/* tp_methods */
  <obj>_members,			/* tp_members */
  <obj>_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  (initproc)<obj>_init,			/* tp_init */
  <obj>_alloc,				/* tp_alloc */
  <obj>_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPI<Obj> C API */

static int
PyMPI<Obj>_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPI<Obj>_Type);
}

static int
PyMPI<Obj>_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPI<Obj>_Type);
}

static PyObject*
PyMPI<Obj>_From<Obj>(MPI_<Obj> <obj>)
{
  PyMPI<Obj>Object *self;
  PyTypeObject *type = &PyMPI<Obj>_Type;
  self = (PyMPI<Obj>Object*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->ob_mpi = (PyObject*) PyObject_New(_Py_MPI_<Obj>,
					    &_Py_MPI_<Obj>_Type);
    if (self->ob_mpi == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPI<Obj>_AS_<OBJ>(self) = <obj>;
  }
  return (PyObject*)self;
}

static MPI_<Obj>
PyMPI<Obj>_As<Obj>(PyObject *self)
{
  if (self) {
    if (PyMPI<Obj>_Check(self))
      return PyMPI<Obj>_AS_<OBJ>(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a '<Obj>' object, "
		 "got %%.200s", Py_TYPE(self)->tp_name);
    return PyMPI_<OBJ>_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPI<Obj>_As<Obj>() called with null pointer");
  return PyMPI_<OBJ>_DEFAULT;
}

static MPI_<Obj>*
PyMPI<Obj>_As<Obj>Ptr(PyObject *self)
{
  if (self) {
    if (PyMPI<Obj>_Check(self))
      return PyMPI<Obj>_AS_<OBJ>_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a '<Obj>' object, "
		 "got %%.200s", Py_TYPE(self)->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPI<Obj>_As<Obj>Ptr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPI<Obj>_TYPE = &PyMPI<Obj>_Type;

static void(*PyMPI<Obj>_API[])(void) =
{
  /*[0]*/ (void(*)(void)) PyMPI<Obj>_Check,
  /*[1]*/ (void(*)(void)) PyMPI<Obj>_CheckExact,
  /*[2]*/ (void(*)(void)) PyMPI<Obj>_From<Obj>,
  /*[4]*/ (void(*)(void)) PyMPI<Obj>_As<Obj>,
  /*[5]*/ (void(*)(void)) PyMPI<Obj>_As<Obj>Ptr,
};
