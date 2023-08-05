/* $Id$ */

#ifndef Py_LIBMPI_H
#define Py_LIBMPI_H

/* Below, some stuff from the top of MPICH2 mpicxx.h ...

   There is a name conflict between stdio.h and the MPI C++ binding 
   with respect to the names SEEK_SET, SEEK_CUR, and SEEK_END.  MPI
   wants these in the MPI namespace, but stdio.h will #define these
   to integer values.  #undef'ing these can cause obscure problems
   with other include files (such as iostream), so we instead use
   #error to indicate a fatal error.  Users can either #undef 
   the names before including mpi.h or include mpi.h *before* stdio.h
   or iostream.

   The MPI STANDARD HAS TO BE CHANGED to prevent this nonsense. 
*/

#include <Python.h>
#include <mpi.h>

#ifdef __cplusplus
extern "C" {
#endif

#if !defined(libmpi_MODULE)

#define libmpi_FatalApiError \
(Py_FatalError("Call to API function without first calling " \
	       "import_libmpi(). [file: " __FILE__ "]"), NULL)

#endif /* !libmpi_MODULE */


#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#if !defined(MPI_INFO_NULL)
#define libmpi_MPI_Info
#define MPI_Info void*
#define MPI_INFO_NULL ((MPI_Info)0)
#endif
#endif

#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#if !defined(MPI_WIN_NULL)
#define libmpi_MPI_Win
#define MPI_Win void*
#define MPI_WIN_NULL ((MPI_Win)0)
#endif
#endif

#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#if !defined(MPI_FILE_NULL)
#define libmpi_MPI_File
#define MPI_File void*
#define MPI_FILE_NULL ((MPI_File)0)
#endif
#endif

<MPI_OBJECT_H>

#if defined(libmpi_MPI_Info)
#undef libmpi_MPI_Info
#undef MPI_Info
#undef MPI_INFO_NULL
#endif

#if defined(libmpi_MPI_Win)
#undef libmpi_MPI_Win
#undef MPI_Win
#undef MPI_WIN_NULL
#endif

#if defined(libmpi_MPI_File)
#undef libmpi_MPI_File
#undef MPI_File
#undef MPI_FILE_NULL
#endif


#if !defined(libmpi_MODULE)

static int import_libmpi(void)
{ 
  PyObject* m = PyImport_ImportModule("mpi4py.libmpi");
  if (m == NULL) return -1;
# define LIBMPI_GET_PYTYPE_AND_CAPI(m,Type) {            \
  PyObject *tp, *api;                                    \
  tp  = PyObject_GetAttrString(m,#Type"Type");           \
  if (tp == NULL) goto fail;                             \
  PyMPI##Type##_TYPE = (PyTypeObject*) tp;               \
  Py_DECREF(tp);                                         \
  api = PyObject_GetAttrString(m,#Type"_API");           \
  if (api == NULL) goto fail;                            \
  PyMPI##Type##_API = (void**) PyCObject_AsVoidPtr(api); \
  Py_DECREF(api);                                        \
  if (PyMPI##Type##_API == NULL) goto fail;              \
  }
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Op         );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Win        );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Comm       );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Info       );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, File       );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Group      );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Status     );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Request    );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Datatype   );
  LIBMPI_GET_PYTYPE_AND_CAPI(m, Errhandler );
# undef LIBMPI_GET_PYTYPE_AND_CAPI
  Py_DECREF(m);
  return 0;
 fail:
  Py_DECREF(m);
  PyErr_Clear();
  PyErr_SetString(PyExc_ImportError,
		  "Can't get MPI types or C API from module 'libmpi'");
  return -1;
}

#endif /* !libmpi_MODULE */


#ifdef __cplusplus
}
#endif

#endif /* !Py_LIBMPI_H */

/* 
 * Local Variables:
 * mode: C
 * End:
 */
