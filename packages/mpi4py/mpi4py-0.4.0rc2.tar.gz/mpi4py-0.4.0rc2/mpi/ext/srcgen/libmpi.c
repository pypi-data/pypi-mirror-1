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

<MPI_OBJECT_C>

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
