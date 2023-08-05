typedef struct _Py_MPI_<Obj> {
  PyObject_HEAD
  MPI_<Obj> <obj>;
} _Py_MPI_<Obj>;

typedef struct PyMPI<Obj>Object {
  PyObject_HEAD
  PyObject* <obj>;
} PyMPI<Obj>Object;

#define PyMPI<Obj>(ob) \
  ((PyMPI<Obj>Object*)(ob))

#define PyMPI<Obj>_AS_<OBJ>(ob) \
  (((_Py_MPI_<Obj>*)(PyMPI<Obj>(ob)-><obj>))-><obj>)

#define PyMPI<Obj>_AS_<OBJ>_PTR(ob) \
  (&PyMPI<Obj>_AS_<OBJ>(ob))


#if defined(libmpi_MODULE)


static int		PyMPI<Obj>_Check(PyObject*);

static int		PyMPI<Obj>_CheckExact(PyObject*);

static PyObject*	PyMPI<Obj>_From<Obj>(MPI_<Obj>);

static MPI_<Obj> 	PyMPI<Obj>_As<Obj>(PyObject*);

static MPI_<Obj>*	PyMPI<Obj>_As<Obj>Ptr(PyObject*);


#else /* !defined(libmpi_MODULE) */


static PyTypeObject*	PyMPI<Obj>_TYPE = NULL;

static void**		PyMPI<Obj>_API  = NULL;

#define PyMPI<Obj>_Type \
((PyMPI<Obj>_TYPE?PyMPI<Obj>_TYPE:(PyTypeObject*)libmpi_FatalApiError))

#define PyMPI<Obj>_Check \
( *(int (*)(PyObject*))  \
  (PyMPI<Obj>_API?PyMPI<Obj>_API[0]:(void*)libmpi_FatalApiError) )

#define PyMPI<Obj>_CheckExact \
( *(int (*)(PyObject*)) \
  (PyMPI<Obj>_API?PyMPI<Obj>_API[1]:(void*)libmpi_FatalApiError) )

#define PyMPI<Obj>_From<Obj> \
( *(PyObject* (*)(MPI_<Obj>)) \
  (PyMPI<Obj>_API?PyMPI<Obj>_API[2]:(void*)libmpi_FatalApiError) )

#define PyMPI<Obj>_As<Obj> \
( *(MPI_<Obj> (*)(PyObject*)) \
  (PyMPI<Obj>_API?PyMPI<Obj>_API[3]:(void*)libmpi_FatalApiError) )

#define PyMPI<Obj>_As<Obj>Ptr \
( *(MPI_<Obj>* (*)(PyObject*)) \
  (PyMPI<Obj>_API?PyMPI<Obj>_API[4]:(void*)libmpi_FatalApiError) )


#endif /* libmpi_MODULE */
