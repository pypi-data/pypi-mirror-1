/* Inner <Obj> Object Structure
 * holds a  MPI_<Obj> handle */

typedef struct _Py_MPI_<Obj> {
  PyObject_HEAD
  MPI_<Obj> <obj>;
  int isref;
} _Py_MPI_<Obj>;

#define PyMPI<Obj>Object PyMPIObject

#define PyMPI<Obj>(ob) \
    ((PyMPI<Obj>Object*)(ob))

#define PyMPI<Obj>_Inner(ob) \
    ((_Py_MPI_<Obj>*)(PyMPI<Obj>(ob)->ob_mpi))

#define PyMPI<Obj>_AS_<OBJ>(ob) \
    (PyMPI<Obj>_Inner(ob)-><obj>)

#define PyMPI<Obj>_AS_<OBJ>_PTR(ob) \
    (&PyMPI<Obj>_AS_<OBJ>(ob))


#if defined(libmpi_MODULE)


static int		PyMPI<Obj>_Check(PyObject*);

static int		PyMPI<Obj>_CheckExact(PyObject*);

static PyObject*	PyMPI<Obj>_From<Obj>(MPI_<Obj>);

static MPI_<Obj> 	PyMPI<Obj>_As<Obj>(PyObject*);

static MPI_<Obj>*	PyMPI<Obj>_As<Obj>Ptr(PyObject*);


#else /* !defined(libmpi_MODULE) */


static PyTypeObject* PyMPI<Obj>_TYPE = 0;

static void (**PyMPI<Obj>_API)(void) = 0;

#define PyMPI<Obj>_Type \
  ((PyTypeObject*)PyMPI<Obj>_TYPE)

#define PyMPI<Obj>_Check \
  (*(int (*)(PyObject*))PyMPI<Obj>_API[0])

#define PyMPI<Obj>_CheckExact \
  (*(int (*)(PyObject*))PyMPI<Obj>_API[1])

#define PyMPI<Obj>_From<Obj> \
  (*(PyObject* (*)(MPI_<Obj>))PyMPI<Obj>_API[2])

#define PyMPI<Obj>_As<Obj> \
  (*(MPI_<Obj> (*)(PyObject*))PyMPI<Obj>_API[3])

#define PyMPI<Obj>_As<Obj>Ptr \
  (*(MPI_<Obj>* (*)(PyObject*))PyMPI<Obj>_API[4])


#endif /* libmpi_MODULE */
