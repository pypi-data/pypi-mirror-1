/* $Id: libmpi.c,v 1.16 2006/11/04 22:15:10 dalcinl Exp $ */

#define MPICH_IGNORE_CXX_SEEK

#define  libmpi_MODULE
#include "libmpi.h"

#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#if !defined(MPI_INFO_NULL)
#define MPI_Info void*
#define MPI_INFO_NULL ((MPI_Info)0)
#endif
#endif

#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#if !defined(MPI_WIN_NULL)
#define MPI_Win void*
#define MPI_WIN_NULL ((MPI_Win)0)
#endif
#endif

#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#if !defined(MPI_FILE_NULL)
#define MPI_File void*
#define MPI_FILE_NULL ((MPI_File)0)
#endif
#endif

/* PyMPIComm_Type implementation */

static PyTypeObject _Py_MPI_Comm_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Comm",		/*tp_name*/
  sizeof(_Py_MPI_Comm),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_COMM_DEFAULT MPI_COMM_NULL

#define comm_alloc PyType_GenericAlloc

static void
comm_dealloc(PyMPICommObject *self)
{
  Py_XDECREF(self->comm);
  self->ob_type->tp_free(self);
}

static PyObject *
comm_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"comm", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Comm", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPICommObject *self;
    self = (PyMPICommObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->comm = (PyObject*) PyObject_New(_Py_MPI_Comm,
					     &_Py_MPI_Comm_Type);
      if (self->comm == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIComm_AS_COMM(self) = MPI_COMM_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIComm_Check(ob)) {
    PyMPICommObject *self;
    self = (PyMPICommObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->comm = ((PyMPICommObject*)ob)->comm;
      if (self->comm == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->comm);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Comm() argument must be a 'Comm' object");
  return NULL;
}

#define comm_init (initproc)0

static long
comm_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Comm' objects are unhashable");
  return -1;
}

static PyObject *
comm_richcompare(PyMPICommObject * o1, PyMPICommObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIComm_Check((PyObject*)o1) && 
	PyMPIComm_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Comm' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIComm_AS_COMM(o1) == PyMPIComm_AS_COMM(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
comm_nonzero(PyMPICommObject* ob) 
{
  return PyMPIComm_AS_COMM(ob) != MPI_COMM_NULL;
}
static PyObject *
comm_hex(PyMPICommObject* ob) 
{
  MPI_Comm comm = PyMPIComm_AS_COMM(ob);
  return PyString_FromFormat("%p", (void *)comm);
}
static PyNumberMethods comm_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)comm_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)comm_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define comm_as_number   &comm_number_methods
#define comm_as_sequence (PySequenceMethods*)0
#define comm_as_mapping  (PyMappingMethods*)0


#define comm_methods 0
#define comm_members 0
#define comm_getset  0


PyDoc_STRVAR(comm_doc, "Comm type");

static PyTypeObject PyMPIComm_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Comm",			        /*tp_name*/
  sizeof(PyMPICommObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)comm_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  comm_as_number,			/*tp_as_number*/
  comm_as_sequence,			/*tp_as_sequence*/
  comm_as_mapping,			/*tp_as_mapping*/

  (hashfunc)comm_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  comm_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)comm_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  comm_methods,			/* tp_methods */
  comm_members,			/* tp_members */
  comm_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  comm_init,				/* tp_init */
  comm_alloc,				/* tp_alloc */
  comm_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIComm C API */

static int
PyMPIComm_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIComm_Type);
}

static int
PyMPIComm_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIComm_Type);
}

static PyObject*
PyMPIComm_FromComm(MPI_Comm comm)
{
  PyMPICommObject *self;
  PyTypeObject *type = &PyMPIComm_Type;
  self = (PyMPICommObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->comm = (PyObject*) PyObject_New(_Py_MPI_Comm,
					   &_Py_MPI_Comm_Type);
    if (self->comm == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIComm_AS_COMM(self) = comm;
  }
  return (PyObject*)self;
}

static MPI_Comm
PyMPIComm_AsComm(PyObject *self)
{
  if (self) {
    if (PyMPIComm_Check(self))
      return PyMPIComm_AS_COMM(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Comm' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_COMM_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIComm_AsComm() called with null pointer");
  return PyMPI_COMM_DEFAULT;
}

static MPI_Comm*
PyMPIComm_AsCommPtr(PyObject *self)
{
  if (self) {
    if (PyMPIComm_Check(self))
      return PyMPIComm_AS_COMM_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Comm' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIComm_AsCommPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIComm_TYPE = &PyMPIComm_Type;

static void* PyMPIComm_API[] = 
{
  /*[0]*/ (void*) PyMPIComm_Check,
  /*[1]*/ (void*) PyMPIComm_CheckExact,
  /*[2]*/ (void*) PyMPIComm_FromComm,
  /*[3]*/ (void*) PyMPIComm_AsComm,
  /*[4]*/ (void*) PyMPIComm_AsCommPtr,
};

/* PyMPIDatatype_Type implementation */

static PyTypeObject _Py_MPI_Datatype_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Datatype",		/*tp_name*/
  sizeof(_Py_MPI_Datatype),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_DATATYPE_DEFAULT MPI_DATATYPE_NULL

#define datatype_alloc PyType_GenericAlloc

static void
datatype_dealloc(PyMPIDatatypeObject *self)
{
  Py_XDECREF(self->datatype);
  self->ob_type->tp_free(self);
}

static PyObject *
datatype_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"datatype", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Datatype", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIDatatypeObject *self;
    self = (PyMPIDatatypeObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->datatype = (PyObject*) PyObject_New(_Py_MPI_Datatype,
					     &_Py_MPI_Datatype_Type);
      if (self->datatype == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIDatatype_AS_DATATYPE(self) = MPI_DATATYPE_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIDatatype_Check(ob)) {
    PyMPIDatatypeObject *self;
    self = (PyMPIDatatypeObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->datatype = ((PyMPIDatatypeObject*)ob)->datatype;
      if (self->datatype == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->datatype);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Datatype() argument must be a 'Datatype' object");
  return NULL;
}

#define datatype_init (initproc)0

static long
datatype_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Datatype' objects are unhashable");
  return -1;
}

static PyObject *
datatype_richcompare(PyMPIDatatypeObject * o1, PyMPIDatatypeObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIDatatype_Check((PyObject*)o1) && 
	PyMPIDatatype_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Datatype' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIDatatype_AS_DATATYPE(o1) == PyMPIDatatype_AS_DATATYPE(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
datatype_nonzero(PyMPIDatatypeObject* ob) 
{
  return PyMPIDatatype_AS_DATATYPE(ob) != MPI_DATATYPE_NULL;
}
static PyObject *
datatype_hex(PyMPIDatatypeObject* ob) 
{
  MPI_Datatype datatype = PyMPIDatatype_AS_DATATYPE(ob);
  return PyString_FromFormat("%p", (void *)datatype);
}
static PyNumberMethods datatype_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)datatype_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)datatype_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define datatype_as_number   &datatype_number_methods
#define datatype_as_sequence (PySequenceMethods*)0
#define datatype_as_mapping  (PyMappingMethods*)0


#define datatype_methods 0
#define datatype_members 0
#define datatype_getset  0


PyDoc_STRVAR(datatype_doc, "Datatype type");

static PyTypeObject PyMPIDatatype_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Datatype",			        /*tp_name*/
  sizeof(PyMPIDatatypeObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)datatype_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  datatype_as_number,			/*tp_as_number*/
  datatype_as_sequence,			/*tp_as_sequence*/
  datatype_as_mapping,			/*tp_as_mapping*/

  (hashfunc)datatype_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  datatype_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)datatype_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  datatype_methods,			/* tp_methods */
  datatype_members,			/* tp_members */
  datatype_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  datatype_init,				/* tp_init */
  datatype_alloc,				/* tp_alloc */
  datatype_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIDatatype C API */

static int
PyMPIDatatype_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIDatatype_Type);
}

static int
PyMPIDatatype_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIDatatype_Type);
}

static PyObject*
PyMPIDatatype_FromDatatype(MPI_Datatype datatype)
{
  PyMPIDatatypeObject *self;
  PyTypeObject *type = &PyMPIDatatype_Type;
  self = (PyMPIDatatypeObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->datatype = (PyObject*) PyObject_New(_Py_MPI_Datatype,
					   &_Py_MPI_Datatype_Type);
    if (self->datatype == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIDatatype_AS_DATATYPE(self) = datatype;
  }
  return (PyObject*)self;
}

static MPI_Datatype
PyMPIDatatype_AsDatatype(PyObject *self)
{
  if (self) {
    if (PyMPIDatatype_Check(self))
      return PyMPIDatatype_AS_DATATYPE(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Datatype' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_DATATYPE_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIDatatype_AsDatatype() called with null pointer");
  return PyMPI_DATATYPE_DEFAULT;
}

static MPI_Datatype*
PyMPIDatatype_AsDatatypePtr(PyObject *self)
{
  if (self) {
    if (PyMPIDatatype_Check(self))
      return PyMPIDatatype_AS_DATATYPE_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Datatype' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIDatatype_AsDatatypePtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIDatatype_TYPE = &PyMPIDatatype_Type;

static void* PyMPIDatatype_API[] = 
{
  /*[0]*/ (void*) PyMPIDatatype_Check,
  /*[1]*/ (void*) PyMPIDatatype_CheckExact,
  /*[2]*/ (void*) PyMPIDatatype_FromDatatype,
  /*[3]*/ (void*) PyMPIDatatype_AsDatatype,
  /*[4]*/ (void*) PyMPIDatatype_AsDatatypePtr,
};

/* PyMPIErrhandler_Type implementation */

static PyTypeObject _Py_MPI_Errhandler_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Errhandler",		/*tp_name*/
  sizeof(_Py_MPI_Errhandler),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_ERRHANDLER_DEFAULT MPI_ERRHANDLER_NULL

#define errhandler_alloc PyType_GenericAlloc

static void
errhandler_dealloc(PyMPIErrhandlerObject *self)
{
  Py_XDECREF(self->errhandler);
  self->ob_type->tp_free(self);
}

static PyObject *
errhandler_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"errhandler", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Errhandler", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIErrhandlerObject *self;
    self = (PyMPIErrhandlerObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->errhandler = (PyObject*) PyObject_New(_Py_MPI_Errhandler,
					     &_Py_MPI_Errhandler_Type);
      if (self->errhandler == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIErrhandler_AS_ERRHANDLER(self) = MPI_ERRHANDLER_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIErrhandler_Check(ob)) {
    PyMPIErrhandlerObject *self;
    self = (PyMPIErrhandlerObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->errhandler = ((PyMPIErrhandlerObject*)ob)->errhandler;
      if (self->errhandler == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->errhandler);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Errhandler() argument must be a 'Errhandler' object");
  return NULL;
}

#define errhandler_init (initproc)0

static long
errhandler_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Errhandler' objects are unhashable");
  return -1;
}

static PyObject *
errhandler_richcompare(PyMPIErrhandlerObject * o1, PyMPIErrhandlerObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIErrhandler_Check((PyObject*)o1) && 
	PyMPIErrhandler_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Errhandler' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIErrhandler_AS_ERRHANDLER(o1) == PyMPIErrhandler_AS_ERRHANDLER(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
errhandler_nonzero(PyMPIErrhandlerObject* ob) 
{
  return PyMPIErrhandler_AS_ERRHANDLER(ob) != MPI_ERRHANDLER_NULL;
}
static PyObject *
errhandler_hex(PyMPIErrhandlerObject* ob) 
{
  MPI_Errhandler errhandler = PyMPIErrhandler_AS_ERRHANDLER(ob);
  return PyString_FromFormat("%p", (void *)errhandler);
}
static PyNumberMethods errhandler_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)errhandler_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)errhandler_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define errhandler_as_number   &errhandler_number_methods
#define errhandler_as_sequence (PySequenceMethods*)0
#define errhandler_as_mapping  (PyMappingMethods*)0


#define errhandler_methods 0
#define errhandler_members 0
#define errhandler_getset  0


PyDoc_STRVAR(errhandler_doc, "Errhandler type");

static PyTypeObject PyMPIErrhandler_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Errhandler",			        /*tp_name*/
  sizeof(PyMPIErrhandlerObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)errhandler_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  errhandler_as_number,			/*tp_as_number*/
  errhandler_as_sequence,			/*tp_as_sequence*/
  errhandler_as_mapping,			/*tp_as_mapping*/

  (hashfunc)errhandler_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  errhandler_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)errhandler_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  errhandler_methods,			/* tp_methods */
  errhandler_members,			/* tp_members */
  errhandler_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  errhandler_init,				/* tp_init */
  errhandler_alloc,				/* tp_alloc */
  errhandler_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIErrhandler C API */

static int
PyMPIErrhandler_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIErrhandler_Type);
}

static int
PyMPIErrhandler_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIErrhandler_Type);
}

static PyObject*
PyMPIErrhandler_FromErrhandler(MPI_Errhandler errhandler)
{
  PyMPIErrhandlerObject *self;
  PyTypeObject *type = &PyMPIErrhandler_Type;
  self = (PyMPIErrhandlerObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->errhandler = (PyObject*) PyObject_New(_Py_MPI_Errhandler,
					   &_Py_MPI_Errhandler_Type);
    if (self->errhandler == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIErrhandler_AS_ERRHANDLER(self) = errhandler;
  }
  return (PyObject*)self;
}

static MPI_Errhandler
PyMPIErrhandler_AsErrhandler(PyObject *self)
{
  if (self) {
    if (PyMPIErrhandler_Check(self))
      return PyMPIErrhandler_AS_ERRHANDLER(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Errhandler' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_ERRHANDLER_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIErrhandler_AsErrhandler() called with null pointer");
  return PyMPI_ERRHANDLER_DEFAULT;
}

static MPI_Errhandler*
PyMPIErrhandler_AsErrhandlerPtr(PyObject *self)
{
  if (self) {
    if (PyMPIErrhandler_Check(self))
      return PyMPIErrhandler_AS_ERRHANDLER_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Errhandler' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIErrhandler_AsErrhandlerPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIErrhandler_TYPE = &PyMPIErrhandler_Type;

static void* PyMPIErrhandler_API[] = 
{
  /*[0]*/ (void*) PyMPIErrhandler_Check,
  /*[1]*/ (void*) PyMPIErrhandler_CheckExact,
  /*[2]*/ (void*) PyMPIErrhandler_FromErrhandler,
  /*[3]*/ (void*) PyMPIErrhandler_AsErrhandler,
  /*[4]*/ (void*) PyMPIErrhandler_AsErrhandlerPtr,
};

/* PyMPIFile_Type implementation */

static PyTypeObject _Py_MPI_File_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_File",		/*tp_name*/
  sizeof(_Py_MPI_File),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_FILE_DEFAULT MPI_FILE_NULL

#define file_alloc PyType_GenericAlloc

static void
file_dealloc(PyMPIFileObject *self)
{
  Py_XDECREF(self->file);
  self->ob_type->tp_free(self);
}

static PyObject *
file_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"file", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:File", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIFileObject *self;
    self = (PyMPIFileObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->file = (PyObject*) PyObject_New(_Py_MPI_File,
					     &_Py_MPI_File_Type);
      if (self->file == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIFile_AS_FILE(self) = MPI_FILE_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIFile_Check(ob)) {
    PyMPIFileObject *self;
    self = (PyMPIFileObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->file = ((PyMPIFileObject*)ob)->file;
      if (self->file == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->file);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "File() argument must be a 'File' object");
  return NULL;
}

#define file_init (initproc)0

static long
file_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'File' objects are unhashable");
  return -1;
}

static PyObject *
file_richcompare(PyMPIFileObject * o1, PyMPIFileObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIFile_Check((PyObject*)o1) && 
	PyMPIFile_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'File' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIFile_AS_FILE(o1) == PyMPIFile_AS_FILE(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
file_nonzero(PyMPIFileObject* ob) 
{
  return PyMPIFile_AS_FILE(ob) != MPI_FILE_NULL;
}
static PyObject *
file_hex(PyMPIFileObject* ob) 
{
  MPI_File file = PyMPIFile_AS_FILE(ob);
  return PyString_FromFormat("%p", (void *)file);
}
static PyNumberMethods file_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)file_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)file_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define file_as_number   &file_number_methods
#define file_as_sequence (PySequenceMethods*)0
#define file_as_mapping  (PyMappingMethods*)0


#define file_methods 0
#define file_members 0
#define file_getset  0


PyDoc_STRVAR(file_doc, "File type");

static PyTypeObject PyMPIFile_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "File",			        /*tp_name*/
  sizeof(PyMPIFileObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)file_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  file_as_number,			/*tp_as_number*/
  file_as_sequence,			/*tp_as_sequence*/
  file_as_mapping,			/*tp_as_mapping*/

  (hashfunc)file_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  file_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)file_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  file_methods,			/* tp_methods */
  file_members,			/* tp_members */
  file_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  file_init,				/* tp_init */
  file_alloc,				/* tp_alloc */
  file_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIFile C API */

static int
PyMPIFile_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIFile_Type);
}

static int
PyMPIFile_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIFile_Type);
}

static PyObject*
PyMPIFile_FromFile(MPI_File file)
{
  PyMPIFileObject *self;
  PyTypeObject *type = &PyMPIFile_Type;
  self = (PyMPIFileObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->file = (PyObject*) PyObject_New(_Py_MPI_File,
					   &_Py_MPI_File_Type);
    if (self->file == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIFile_AS_FILE(self) = file;
  }
  return (PyObject*)self;
}

static MPI_File
PyMPIFile_AsFile(PyObject *self)
{
  if (self) {
    if (PyMPIFile_Check(self))
      return PyMPIFile_AS_FILE(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'File' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_FILE_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIFile_AsFile() called with null pointer");
  return PyMPI_FILE_DEFAULT;
}

static MPI_File*
PyMPIFile_AsFilePtr(PyObject *self)
{
  if (self) {
    if (PyMPIFile_Check(self))
      return PyMPIFile_AS_FILE_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'File' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIFile_AsFilePtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIFile_TYPE = &PyMPIFile_Type;

static void* PyMPIFile_API[] = 
{
  /*[0]*/ (void*) PyMPIFile_Check,
  /*[1]*/ (void*) PyMPIFile_CheckExact,
  /*[2]*/ (void*) PyMPIFile_FromFile,
  /*[3]*/ (void*) PyMPIFile_AsFile,
  /*[4]*/ (void*) PyMPIFile_AsFilePtr,
};

/* PyMPIGroup_Type implementation */

static PyTypeObject _Py_MPI_Group_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Group",		/*tp_name*/
  sizeof(_Py_MPI_Group),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_GROUP_DEFAULT MPI_GROUP_NULL

#define group_alloc PyType_GenericAlloc

static void
group_dealloc(PyMPIGroupObject *self)
{
  Py_XDECREF(self->group);
  self->ob_type->tp_free(self);
}

static PyObject *
group_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"group", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Group", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIGroupObject *self;
    self = (PyMPIGroupObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->group = (PyObject*) PyObject_New(_Py_MPI_Group,
					     &_Py_MPI_Group_Type);
      if (self->group == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIGroup_AS_GROUP(self) = MPI_GROUP_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIGroup_Check(ob)) {
    PyMPIGroupObject *self;
    self = (PyMPIGroupObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->group = ((PyMPIGroupObject*)ob)->group;
      if (self->group == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->group);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Group() argument must be a 'Group' object");
  return NULL;
}

#define group_init (initproc)0

static long
group_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Group' objects are unhashable");
  return -1;
}

static PyObject *
group_richcompare(PyMPIGroupObject * o1, PyMPIGroupObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIGroup_Check((PyObject*)o1) && 
	PyMPIGroup_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Group' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIGroup_AS_GROUP(o1) == PyMPIGroup_AS_GROUP(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
group_nonzero(PyMPIGroupObject* ob) 
{
  return PyMPIGroup_AS_GROUP(ob) != MPI_GROUP_NULL;
}
static PyObject *
group_hex(PyMPIGroupObject* ob) 
{
  MPI_Group group = PyMPIGroup_AS_GROUP(ob);
  return PyString_FromFormat("%p", (void *)group);
}
static PyNumberMethods group_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)group_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)group_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define group_as_number   &group_number_methods
#define group_as_sequence (PySequenceMethods*)0
#define group_as_mapping  (PyMappingMethods*)0


#define group_methods 0
#define group_members 0
#define group_getset  0


PyDoc_STRVAR(group_doc, "Group type");

static PyTypeObject PyMPIGroup_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Group",			        /*tp_name*/
  sizeof(PyMPIGroupObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)group_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  group_as_number,			/*tp_as_number*/
  group_as_sequence,			/*tp_as_sequence*/
  group_as_mapping,			/*tp_as_mapping*/

  (hashfunc)group_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  group_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)group_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  group_methods,			/* tp_methods */
  group_members,			/* tp_members */
  group_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  group_init,				/* tp_init */
  group_alloc,				/* tp_alloc */
  group_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIGroup C API */

static int
PyMPIGroup_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIGroup_Type);
}

static int
PyMPIGroup_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIGroup_Type);
}

static PyObject*
PyMPIGroup_FromGroup(MPI_Group group)
{
  PyMPIGroupObject *self;
  PyTypeObject *type = &PyMPIGroup_Type;
  self = (PyMPIGroupObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->group = (PyObject*) PyObject_New(_Py_MPI_Group,
					   &_Py_MPI_Group_Type);
    if (self->group == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIGroup_AS_GROUP(self) = group;
  }
  return (PyObject*)self;
}

static MPI_Group
PyMPIGroup_AsGroup(PyObject *self)
{
  if (self) {
    if (PyMPIGroup_Check(self))
      return PyMPIGroup_AS_GROUP(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Group' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_GROUP_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIGroup_AsGroup() called with null pointer");
  return PyMPI_GROUP_DEFAULT;
}

static MPI_Group*
PyMPIGroup_AsGroupPtr(PyObject *self)
{
  if (self) {
    if (PyMPIGroup_Check(self))
      return PyMPIGroup_AS_GROUP_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Group' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIGroup_AsGroupPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIGroup_TYPE = &PyMPIGroup_Type;

static void* PyMPIGroup_API[] = 
{
  /*[0]*/ (void*) PyMPIGroup_Check,
  /*[1]*/ (void*) PyMPIGroup_CheckExact,
  /*[2]*/ (void*) PyMPIGroup_FromGroup,
  /*[3]*/ (void*) PyMPIGroup_AsGroup,
  /*[4]*/ (void*) PyMPIGroup_AsGroupPtr,
};

/* PyMPIInfo_Type implementation */

static PyTypeObject _Py_MPI_Info_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Info",		/*tp_name*/
  sizeof(_Py_MPI_Info),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_INFO_DEFAULT MPI_INFO_NULL

#define info_alloc PyType_GenericAlloc

static void
info_dealloc(PyMPIInfoObject *self)
{
  Py_XDECREF(self->info);
  self->ob_type->tp_free(self);
}

static PyObject *
info_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"info", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Info", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIInfoObject *self;
    self = (PyMPIInfoObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->info = (PyObject*) PyObject_New(_Py_MPI_Info,
					     &_Py_MPI_Info_Type);
      if (self->info == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIInfo_AS_INFO(self) = MPI_INFO_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIInfo_Check(ob)) {
    PyMPIInfoObject *self;
    self = (PyMPIInfoObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->info = ((PyMPIInfoObject*)ob)->info;
      if (self->info == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->info);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Info() argument must be a 'Info' object");
  return NULL;
}

#define info_init (initproc)0

static long
info_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Info' objects are unhashable");
  return -1;
}

static PyObject *
info_richcompare(PyMPIInfoObject * o1, PyMPIInfoObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIInfo_Check((PyObject*)o1) && 
	PyMPIInfo_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Info' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIInfo_AS_INFO(o1) == PyMPIInfo_AS_INFO(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
info_nonzero(PyMPIInfoObject* ob) 
{
  return PyMPIInfo_AS_INFO(ob) != MPI_INFO_NULL;
}
static PyObject *
info_hex(PyMPIInfoObject* ob) 
{
  MPI_Info info = PyMPIInfo_AS_INFO(ob);
  return PyString_FromFormat("%p", (void *)info);
}
static PyNumberMethods info_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)info_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)info_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define info_as_number   &info_number_methods
#define info_as_sequence (PySequenceMethods*)0
#define info_as_mapping  (PyMappingMethods*)0


#define info_methods 0
#define info_members 0
#define info_getset  0


PyDoc_STRVAR(info_doc, "Info type");

static PyTypeObject PyMPIInfo_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Info",			        /*tp_name*/
  sizeof(PyMPIInfoObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)info_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  info_as_number,			/*tp_as_number*/
  info_as_sequence,			/*tp_as_sequence*/
  info_as_mapping,			/*tp_as_mapping*/

  (hashfunc)info_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  info_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)info_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  info_methods,			/* tp_methods */
  info_members,			/* tp_members */
  info_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  info_init,				/* tp_init */
  info_alloc,				/* tp_alloc */
  info_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIInfo C API */

static int
PyMPIInfo_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIInfo_Type);
}

static int
PyMPIInfo_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIInfo_Type);
}

static PyObject*
PyMPIInfo_FromInfo(MPI_Info info)
{
  PyMPIInfoObject *self;
  PyTypeObject *type = &PyMPIInfo_Type;
  self = (PyMPIInfoObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->info = (PyObject*) PyObject_New(_Py_MPI_Info,
					   &_Py_MPI_Info_Type);
    if (self->info == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIInfo_AS_INFO(self) = info;
  }
  return (PyObject*)self;
}

static MPI_Info
PyMPIInfo_AsInfo(PyObject *self)
{
  if (self) {
    if (PyMPIInfo_Check(self))
      return PyMPIInfo_AS_INFO(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Info' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_INFO_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIInfo_AsInfo() called with null pointer");
  return PyMPI_INFO_DEFAULT;
}

static MPI_Info*
PyMPIInfo_AsInfoPtr(PyObject *self)
{
  if (self) {
    if (PyMPIInfo_Check(self))
      return PyMPIInfo_AS_INFO_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Info' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIInfo_AsInfoPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIInfo_TYPE = &PyMPIInfo_Type;

static void* PyMPIInfo_API[] = 
{
  /*[0]*/ (void*) PyMPIInfo_Check,
  /*[1]*/ (void*) PyMPIInfo_CheckExact,
  /*[2]*/ (void*) PyMPIInfo_FromInfo,
  /*[3]*/ (void*) PyMPIInfo_AsInfo,
  /*[4]*/ (void*) PyMPIInfo_AsInfoPtr,
};

/* PyMPIOp_Type implementation */

static PyTypeObject _Py_MPI_Op_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Op",		/*tp_name*/
  sizeof(_Py_MPI_Op),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_OP_DEFAULT MPI_OP_NULL

#define op_alloc PyType_GenericAlloc

static void
op_dealloc(PyMPIOpObject *self)
{
  Py_XDECREF(self->op);
  self->ob_type->tp_free(self);
}

static PyObject *
op_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"op", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Op", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIOpObject *self;
    self = (PyMPIOpObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->op = (PyObject*) PyObject_New(_Py_MPI_Op,
					     &_Py_MPI_Op_Type);
      if (self->op == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIOp_AS_OP(self) = MPI_OP_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIOp_Check(ob)) {
    PyMPIOpObject *self;
    self = (PyMPIOpObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->op = ((PyMPIOpObject*)ob)->op;
      if (self->op == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->op);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Op() argument must be a 'Op' object");
  return NULL;
}

#define op_init (initproc)0

static long
op_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Op' objects are unhashable");
  return -1;
}

static PyObject *
op_richcompare(PyMPIOpObject * o1, PyMPIOpObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIOp_Check((PyObject*)o1) && 
	PyMPIOp_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Op' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIOp_AS_OP(o1) == PyMPIOp_AS_OP(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
op_nonzero(PyMPIOpObject* ob) 
{
  return PyMPIOp_AS_OP(ob) != MPI_OP_NULL;
}
static PyObject *
op_hex(PyMPIOpObject* ob) 
{
  MPI_Op op = PyMPIOp_AS_OP(ob);
  return PyString_FromFormat("%p", (void *)op);
}
static PyNumberMethods op_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)op_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)op_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define op_as_number   &op_number_methods
#define op_as_sequence (PySequenceMethods*)0
#define op_as_mapping  (PyMappingMethods*)0


#define op_methods 0
#define op_members 0
#define op_getset  0


PyDoc_STRVAR(op_doc, "Op type");

static PyTypeObject PyMPIOp_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Op",			        /*tp_name*/
  sizeof(PyMPIOpObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)op_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  op_as_number,			/*tp_as_number*/
  op_as_sequence,			/*tp_as_sequence*/
  op_as_mapping,			/*tp_as_mapping*/

  (hashfunc)op_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  op_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)op_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  op_methods,			/* tp_methods */
  op_members,			/* tp_members */
  op_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  op_init,				/* tp_init */
  op_alloc,				/* tp_alloc */
  op_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIOp C API */

static int
PyMPIOp_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIOp_Type);
}

static int
PyMPIOp_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIOp_Type);
}

static PyObject*
PyMPIOp_FromOp(MPI_Op op)
{
  PyMPIOpObject *self;
  PyTypeObject *type = &PyMPIOp_Type;
  self = (PyMPIOpObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->op = (PyObject*) PyObject_New(_Py_MPI_Op,
					   &_Py_MPI_Op_Type);
    if (self->op == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIOp_AS_OP(self) = op;
  }
  return (PyObject*)self;
}

static MPI_Op
PyMPIOp_AsOp(PyObject *self)
{
  if (self) {
    if (PyMPIOp_Check(self))
      return PyMPIOp_AS_OP(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Op' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_OP_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIOp_AsOp() called with null pointer");
  return PyMPI_OP_DEFAULT;
}

static MPI_Op*
PyMPIOp_AsOpPtr(PyObject *self)
{
  if (self) {
    if (PyMPIOp_Check(self))
      return PyMPIOp_AS_OP_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Op' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIOp_AsOpPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIOp_TYPE = &PyMPIOp_Type;

static void* PyMPIOp_API[] = 
{
  /*[0]*/ (void*) PyMPIOp_Check,
  /*[1]*/ (void*) PyMPIOp_CheckExact,
  /*[2]*/ (void*) PyMPIOp_FromOp,
  /*[3]*/ (void*) PyMPIOp_AsOp,
  /*[4]*/ (void*) PyMPIOp_AsOpPtr,
};

/* PyMPIRequest_Type implementation */

static PyTypeObject _Py_MPI_Request_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Request",		/*tp_name*/
  sizeof(_Py_MPI_Request),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_REQUEST_DEFAULT MPI_REQUEST_NULL

#define request_alloc PyType_GenericAlloc

static void
request_dealloc(PyMPIRequestObject *self)
{
  Py_XDECREF(self->request);
  self->ob_type->tp_free(self);
}

static PyObject *
request_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"request", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Request", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIRequestObject *self;
    self = (PyMPIRequestObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->request = (PyObject*) PyObject_New(_Py_MPI_Request,
					     &_Py_MPI_Request_Type);
      if (self->request == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIRequest_AS_REQUEST(self) = MPI_REQUEST_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIRequest_Check(ob)) {
    PyMPIRequestObject *self;
    self = (PyMPIRequestObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->request = ((PyMPIRequestObject*)ob)->request;
      if (self->request == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->request);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Request() argument must be a 'Request' object");
  return NULL;
}

#define request_init (initproc)0

static long
request_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Request' objects are unhashable");
  return -1;
}

static PyObject *
request_richcompare(PyMPIRequestObject * o1, PyMPIRequestObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIRequest_Check((PyObject*)o1) && 
	PyMPIRequest_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Request' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIRequest_AS_REQUEST(o1) == PyMPIRequest_AS_REQUEST(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
request_nonzero(PyMPIRequestObject* ob) 
{
  return PyMPIRequest_AS_REQUEST(ob) != MPI_REQUEST_NULL;
}
static PyObject *
request_hex(PyMPIRequestObject* ob) 
{
  MPI_Request request = PyMPIRequest_AS_REQUEST(ob);
  return PyString_FromFormat("%p", (void *)request);
}
static PyNumberMethods request_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)request_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)request_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define request_as_number   &request_number_methods
#define request_as_sequence (PySequenceMethods*)0
#define request_as_mapping  (PyMappingMethods*)0


#define request_methods 0
#define request_members 0
#define request_getset  0


PyDoc_STRVAR(request_doc, "Request type");

static PyTypeObject PyMPIRequest_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Request",			        /*tp_name*/
  sizeof(PyMPIRequestObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)request_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  request_as_number,			/*tp_as_number*/
  request_as_sequence,			/*tp_as_sequence*/
  request_as_mapping,			/*tp_as_mapping*/

  (hashfunc)request_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  request_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)request_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  request_methods,			/* tp_methods */
  request_members,			/* tp_members */
  request_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  request_init,				/* tp_init */
  request_alloc,				/* tp_alloc */
  request_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIRequest C API */

static int
PyMPIRequest_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIRequest_Type);
}

static int
PyMPIRequest_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIRequest_Type);
}

static PyObject*
PyMPIRequest_FromRequest(MPI_Request request)
{
  PyMPIRequestObject *self;
  PyTypeObject *type = &PyMPIRequest_Type;
  self = (PyMPIRequestObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->request = (PyObject*) PyObject_New(_Py_MPI_Request,
					   &_Py_MPI_Request_Type);
    if (self->request == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIRequest_AS_REQUEST(self) = request;
  }
  return (PyObject*)self;
}

static MPI_Request
PyMPIRequest_AsRequest(PyObject *self)
{
  if (self) {
    if (PyMPIRequest_Check(self))
      return PyMPIRequest_AS_REQUEST(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Request' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_REQUEST_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIRequest_AsRequest() called with null pointer");
  return PyMPI_REQUEST_DEFAULT;
}

static MPI_Request*
PyMPIRequest_AsRequestPtr(PyObject *self)
{
  if (self) {
    if (PyMPIRequest_Check(self))
      return PyMPIRequest_AS_REQUEST_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Request' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIRequest_AsRequestPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIRequest_TYPE = &PyMPIRequest_Type;

static void* PyMPIRequest_API[] = 
{
  /*[0]*/ (void*) PyMPIRequest_Check,
  /*[1]*/ (void*) PyMPIRequest_CheckExact,
  /*[2]*/ (void*) PyMPIRequest_FromRequest,
  /*[3]*/ (void*) PyMPIRequest_AsRequest,
  /*[4]*/ (void*) PyMPIRequest_AsRequestPtr,
};

/* PyMPIStatus_Type implementation */

static PyTypeObject _Py_MPI_Status_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Status",		/*tp_name*/
  sizeof(_Py_MPI_Status),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


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

#define status_alloc PyType_GenericAlloc

static void
status_dealloc(PyMPIStatusObject *self)
{
  Py_XDECREF(self->status);
  self->ob_type->tp_free(self);
}

static PyObject *
status_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"status", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Status", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIStatusObject *self;
    self = (PyMPIStatusObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->status = (PyObject*) PyObject_New(_Py_MPI_Status,
					     &_Py_MPI_Status_Type);
      if (self->status == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      status_set_empty(PyMPIStatus_AS_STATUS_PTR(self));
    }
    return (PyObject*)self;
  }
  
  if (PyMPIStatus_Check(ob)) {
    PyMPIStatusObject *self;
    self = (PyMPIStatusObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->status = (PyObject*) PyObject_New(_Py_MPI_Status,
					      &_Py_MPI_Status_Type);
      if (self->status == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIStatus_AS_STATUS(self) = PyMPIStatus_AS_STATUS(ob);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Status() argument must be a 'Status' object");
  return NULL;
}

#define status_init (initproc)0

static long
status_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Status' objects are unhashable");
  return -1;
}

static PyObject *
status_richcompare(PyMPIStatusObject * o1, PyMPIStatusObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIStatus_Check((PyObject*)o1) && 
	PyMPIStatus_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  PyErr_SetString(PyExc_TypeError,
		  "cannot compare 'Status' objects");
  res = NULL;
  return res;
}



#define status_as_number   (PyNumberMethods*)0
#define status_as_sequence (PySequenceMethods*)0
#define status_as_mapping  (PyMappingMethods*)0


#define status_methods 0
#define status_members 0
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


PyDoc_STRVAR(status_doc, "Status type");

static PyTypeObject PyMPIStatus_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Status",			        /*tp_name*/
  sizeof(PyMPIStatusObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)status_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  status_as_number,			/*tp_as_number*/
  status_as_sequence,			/*tp_as_sequence*/
  status_as_mapping,			/*tp_as_mapping*/

  (hashfunc)status_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  status_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)status_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  status_methods,			/* tp_methods */
  status_members,			/* tp_members */
  status_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  status_init,				/* tp_init */
  status_alloc,				/* tp_alloc */
  status_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIStatus C API */

static int
PyMPIStatus_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIStatus_Type);
}

static int
PyMPIStatus_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIStatus_Type);
}

static PyObject*
PyMPIStatus_FromStatus(MPI_Status status)
{
  PyMPIStatusObject *self;
  PyTypeObject *type = &PyMPIStatus_Type;
  self = (PyMPIStatusObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->status = (PyObject*) PyObject_New(_Py_MPI_Status,
					   &_Py_MPI_Status_Type);
    if (self->status == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIStatus_AS_STATUS(self) = status;
  }
  return (PyObject*)self;
}

static MPI_Status
PyMPIStatus_AsStatus(PyObject *self)
{
  if (self) {
    if (PyMPIStatus_Check(self))
      return PyMPIStatus_AS_STATUS(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Status' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_STATUS_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIStatus_AsStatus() called with null pointer");
  return PyMPI_STATUS_DEFAULT;
}

static MPI_Status*
PyMPIStatus_AsStatusPtr(PyObject *self)
{
  if (self) {
    if (PyMPIStatus_Check(self))
      return PyMPIStatus_AS_STATUS_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Status' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIStatus_AsStatusPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIStatus_TYPE = &PyMPIStatus_Type;

static void* PyMPIStatus_API[] = 
{
  /*[0]*/ (void*) PyMPIStatus_Check,
  /*[1]*/ (void*) PyMPIStatus_CheckExact,
  /*[2]*/ (void*) PyMPIStatus_FromStatus,
  /*[3]*/ (void*) PyMPIStatus_AsStatus,
  /*[4]*/ (void*) PyMPIStatus_AsStatusPtr,
};

/* PyMPIWin_Type implementation */

static PyTypeObject _Py_MPI_Win_Type = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "_Py_MPI_Win",		/*tp_name*/
  sizeof(_Py_MPI_Win),	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  (destructor)PyObject_Del,	/*tp_dealloc*/
  0,
};


#define PyMPI_WIN_DEFAULT MPI_WIN_NULL

#define win_alloc PyType_GenericAlloc

static void
win_dealloc(PyMPIWinObject *self)
{
  Py_XDECREF(self->win);
  self->ob_type->tp_free(self);
}

static PyObject *
win_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyObject *ob = NULL;
  static char *kwlist[] = {"win", 0};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				   "|O:Win", kwlist,
				   &ob)) return NULL;
  
  if (ob == NULL || ob == Py_None) {
    PyMPIWinObject *self;
    self = (PyMPIWinObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->win = (PyObject*) PyObject_New(_Py_MPI_Win,
					     &_Py_MPI_Win_Type);
      if (self->win == NULL) {
	Py_DECREF(self);
	return NULL;
      }
      PyMPIWin_AS_WIN(self) = MPI_WIN_NULL;
    }
    return (PyObject*)self;
  }
  
  if (ob->ob_type == type) {
    Py_INCREF(ob);
    return ob;
  }

  if (PyMPIWin_Check(ob)) {
    PyMPIWinObject *self;
    self = (PyMPIWinObject*) type->tp_alloc(type, 0);
    if (self != NULL) {
      self->win = ((PyMPIWinObject*)ob)->win;
      if (self->win == NULL) {
	Py_DECREF(self);
	PyErr_BadInternalCall();
	return NULL;
      }
      Py_INCREF(self->win);
    }
    return (PyObject*) self;
  }
  
  PyErr_SetString(PyExc_TypeError,
		  "Win() argument must be a 'Win' object");
  return NULL;
}

#define win_init (initproc)0

static long
win_nohash(PyObject *self)
{
  PyErr_SetString(PyExc_TypeError, "'Win' objects are unhashable");
  return -1;
}

static PyObject *
win_richcompare(PyMPIWinObject * o1, PyMPIWinObject * o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyMPIWin_Check((PyObject*)o1) && 
	PyMPIWin_Check((PyObject*)o2))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare 'Win' objects using <, <=, >, >=");
    return NULL;
  }

  if ((op == Py_EQ) == 
      (PyMPIWin_AS_WIN(o1) == PyMPIWin_AS_WIN(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}



static int
win_nonzero(PyMPIWinObject* ob) 
{
  return PyMPIWin_AS_WIN(ob) != MPI_WIN_NULL;
}
static PyObject *
win_hex(PyMPIWinObject* ob) 
{
  MPI_Win win = PyMPIWin_AS_WIN(ob);
  return PyString_FromFormat("%p", (void *)win);
}
static PyNumberMethods win_number_methods = {
	0,			/*nb_add*/
	0,			/*nb_subtract*/
	0,			/*nb_multiply*/
	0, 	 	 	/*nb_divide*/
	0,			/*nb_remainder*/
	0,			/*nb_divmod*/
	0,			/*nb_power*/
	0,			/*nb_negative*/
	0,			/*nb_positive*/
	0,			/*nb_absolute*/
	(inquiry)win_nonzero,	/*nb_nonzero*/
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
	(unaryfunc)win_hex, 	/*nb_hex*/
	0,			/*nb_inplace_add*/
	0,			/*nb_inplace_subtract*/
	0,			/*nb_inplace_multiply*/
	0,			/*nb_inplace_divide*/
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
#define win_as_number   &win_number_methods
#define win_as_sequence (PySequenceMethods*)0
#define win_as_mapping  (PyMappingMethods*)0


#define win_methods 0
#define win_members 0
#define win_getset  0


PyDoc_STRVAR(win_doc, "Win type");

static PyTypeObject PyMPIWin_Type = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "Win",			        /*tp_name*/
  sizeof(PyMPIWinObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)win_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)0,				/*tp_repr*/

  win_as_number,			/*tp_as_number*/
  win_as_sequence,			/*tp_as_sequence*/
  win_as_mapping,			/*tp_as_mapping*/

  (hashfunc)win_nohash,		/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  win_doc, 				/*tp_doc*/

  (traverseproc)0,			/* tp_traverse */

  (inquiry)0,				/* tp_clear */

  (richcmpfunc)win_richcompare,	/* tp_richcompare */

  (long)0,				/* tp_weaklistoffset */

  (getiterfunc)0,			/* tp_iter */
  (iternextfunc)0,			/* tp_iternext */

  win_methods,			/* tp_methods */
  win_members,			/* tp_members */
  win_getset,				/* tp_getset */
  0,					/* tp_base */
  0,					/* tp_dict */
  (descrgetfunc)0,			/* tp_descr_get */
  (descrsetfunc)0,			/* tp_descr_set */
  (long)0,				/* tp_dictoffset */

  win_init,				/* tp_init */
  win_alloc,				/* tp_alloc */
  win_new,				/* tp_new */
  PyObject_Del,           		/* tp_free */
};



/* PyMPIWin C API */

static int
PyMPIWin_Check(PyObject *op)
{
  return PyObject_TypeCheck(op, &PyMPIWin_Type);
}

static int
PyMPIWin_CheckExact(PyObject *op)
{
  return ((op)->ob_type == &PyMPIWin_Type);
}

static PyObject*
PyMPIWin_FromWin(MPI_Win win)
{
  PyMPIWinObject *self;
  PyTypeObject *type = &PyMPIWin_Type;
  self = (PyMPIWinObject*) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->win = (PyObject*) PyObject_New(_Py_MPI_Win,
					   &_Py_MPI_Win_Type);
    if (self->win == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    PyMPIWin_AS_WIN(self) = win;
  }
  return (PyObject*)self;
}

static MPI_Win
PyMPIWin_AsWin(PyObject *self)
{
  if (self) {
    if (PyMPIWin_Check(self))
      return PyMPIWin_AS_WIN(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Win' object, "
		 "got %.200s", self->ob_type->tp_name);
    return PyMPI_WIN_DEFAULT;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIWin_AsWin() called with null pointer");
  return PyMPI_WIN_DEFAULT;
}

static MPI_Win*
PyMPIWin_AsWinPtr(PyObject *self)
{
  if (self) {
    if (PyMPIWin_Check(self))
      return PyMPIWin_AS_WIN_PTR(self);
    PyErr_Format(PyExc_TypeError,
		 "expecting a 'Win' object, "
		 "got %.200s", self->ob_type->tp_name);
    return NULL;
  }
  PyErr_SetString(PyExc_TypeError,
		  "PyMPIWin_AsWinPtr() called with null pointer");
  return NULL;
}


/* API pointers to export */

static PyTypeObject* PyMPIWin_TYPE = &PyMPIWin_Type;

static void* PyMPIWin_API[] = 
{
  /*[0]*/ (void*) PyMPIWin_Check,
  /*[1]*/ (void*) PyMPIWin_CheckExact,
  /*[2]*/ (void*) PyMPIWin_FromWin,
  /*[3]*/ (void*) PyMPIWin_AsWin,
  /*[4]*/ (void*) PyMPIWin_AsWinPtr,
};


/*------------------------------------------------------------------*/

/* Helper macro to initialize MPI types */
#define LIBMPI_TYPE_INIT(Type)                          \
do {                                                    \
  _Py_MPI_##Type##_Type.ob_type = &PyType_Type;		\
  PyMPI##Type##_Type.ob_type = &PyType_Type;		\
  if (PyType_Ready(&_Py_MPI_##Type##_Type) < 0) return; \
  if (PyType_Ready(&PyMPI##Type##_Type)    < 0) return; \
} while(0)

/* Helper macro to add MPI types and API pointers */
#define LIBMPI_TYPE_ADD(m, Type)                                         \
do {                                                                     \
  PyObject* tp  = (PyObject*) PyMPI##Type##_TYPE;                        \
  PyObject* api = PyCObject_FromVoidPtr((void*)PyMPI##Type##_API, NULL); \
  if (api == NULL) return;                                               \
  if (PyModule_AddObject(m, #Type"Type", tp)  < 0) return;               \
  if (PyModule_AddObject(m, #Type"_API", api) < 0) return;               \
} while(0)

/*------------------------------------------------------------------*/

PyDoc_STRVAR(libmpi_doc, "MPI Basic Types and C API");

static struct PyMethodDef libmpi_methods[] = 
{
  {NULL, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initlibmpi(void) 
{
  PyObject* m;

  LIBMPI_TYPE_INIT( Op         );
  LIBMPI_TYPE_INIT( Win        );
  LIBMPI_TYPE_INIT( Comm       );
  LIBMPI_TYPE_INIT( Info       );
  LIBMPI_TYPE_INIT( File       );
  LIBMPI_TYPE_INIT( Group      );
  LIBMPI_TYPE_INIT( Status     );
  LIBMPI_TYPE_INIT( Request    );
  LIBMPI_TYPE_INIT( Datatype   );
  LIBMPI_TYPE_INIT( Errhandler );
  
  m = Py_InitModule4("mpi4py.libmpi",
		     libmpi_methods, libmpi_doc,
		     NULL, PYTHON_API_VERSION);
  if (m == NULL) return;

  LIBMPI_TYPE_ADD(m, Op         );
  LIBMPI_TYPE_ADD(m, Win        );
  LIBMPI_TYPE_ADD(m, Comm       );
  LIBMPI_TYPE_ADD(m, Info       );
  LIBMPI_TYPE_ADD(m, File       );
  LIBMPI_TYPE_ADD(m, Group      );
  LIBMPI_TYPE_ADD(m, Status     );
  LIBMPI_TYPE_ADD(m, Request    );
  LIBMPI_TYPE_ADD(m, Datatype   );
  LIBMPI_TYPE_ADD(m, Errhandler );

}

/*------------------------------------------------------------------*/

/* 
 * Local Variables:
 * mode: C
 * End:
 */
