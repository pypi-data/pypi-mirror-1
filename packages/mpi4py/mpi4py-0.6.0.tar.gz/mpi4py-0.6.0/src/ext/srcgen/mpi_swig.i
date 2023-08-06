/* $Id$ */

%module _mpi_swig

%header %{
#define MPICH_IGNORE_CXX_SEEK
#include "libmpi.h"
%}

%header %{
#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#ifndef MPI_INFO_NULL
#define MPI_Info void*
#define MPI_INFO_NULL ((MPI_Info)0)
#endif
#endif
%}

%header %{
#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#ifndef MPI_WIN_NULL
#define MPI_Win void*
#define MPI_WIN_NULL ((MPI_Win)0)
#endif
#endif
%}

%header %{
#if !defined(MPI_VERSION) || (MPI_VERSION < 2)
#ifndef MPI_FILE_NULL
#define MPI_File void*
#define MPI_FILE_NULL ((MPI_File)0)
#endif
#endif
%}

%init %{
import_libmpi();
%}

%runtime %{
SWIGINTERNINLINE PyObject*
MPI4PY_SWIG_GetThis(PyObject* obj) {
  if (!obj) return NULL;
  obj = PyObject_GetAttr(obj, SWIG_This());
  if (!obj) PyErr_Clear();
  return obj;
}
SWIGINTERNINLINE int
MPI4PY_SWIG_ConvertPtr(PyObject *obj, void **ptr,
		       swig_type_info *ty, int flags) {
  int res = SWIG_ConvertPtr(obj, ptr, ty, flags);
  if (!SWIG_IsOK(res)) {
    PyObject* _this = MPI4PY_SWIG_GetThis(obj);
    res = SWIG_ConvertPtr(_this, ptr, ty, flags);
    Py_XDECREF(_this);
  }
  return res;
}
#undef  SWIG_ConvertPtr
#define SWIG_ConvertPtr(obj, pptr, type, flags) \
        MPI4PY_SWIG_ConvertPtr(obj, pptr, type, flags)
%}

%define MPI_OBJECT_TYPEMAP(MPI_Object, MPI_OBJECT_DEFAULT)
%types(MPI_Object);
#if #MPI_Object != "MPI_Status"
%typemap(arginit, noblock=1) MPI_Object { $1 = MPI_OBJECT_DEFAULT; };
#endif
%enddef /* MPI_OBJECT_TYPEMAP */

MPI_OBJECT_TYPEMAP(MPI_Op        , MPI_OP_NULL);
MPI_OBJECT_TYPEMAP(MPI_Win       , MPI_WIN_NULL);
MPI_OBJECT_TYPEMAP(MPI_Comm      , MPI_COMM_NULL);
MPI_OBJECT_TYPEMAP(MPI_Info      , MPI_INFO_NULL);
MPI_OBJECT_TYPEMAP(MPI_File      , MPI_FILE_NULL);
MPI_OBJECT_TYPEMAP(MPI_Group     , MPI_GROUP_NULL);
MPI_OBJECT_TYPEMAP(MPI_Status    , MPI_STATUS_IGNORE);
MPI_OBJECT_TYPEMAP(MPI_Request   , MPI_REQUEST_NULL);
MPI_OBJECT_TYPEMAP(MPI_Datatype  , MPI_DATATYPE_NULL);
MPI_OBJECT_TYPEMAP(MPI_Errhandler, MPI_ERRHANDLER_NULL);

%define MPI4PY_SWIGPTR(Type)
%rename(as_##Type) PyMPI##Type##_As##Type##Ptr;
%exception PyMPI##Type##_As##Type##Ptr
"$action if (PyErr_Occurred()) SWIG_fail;"
MPI_##Type* PyMPI##Type##_As##Type##Ptr(PyObject*);
%rename(from_##Type) PyMPI##Type##_From##Type;
PyObject* PyMPI##Type##_From##Type(MPI_##Type);
%enddef /* MPI4PY_SWIGPTR */

MPI4PY_SWIGPTR(Op         );
MPI4PY_SWIGPTR(Win        );
MPI4PY_SWIGPTR(Comm       );
MPI4PY_SWIGPTR(Info       );
MPI4PY_SWIGPTR(File       );
MPI4PY_SWIGPTR(Group      );
MPI4PY_SWIGPTR(Status     );
MPI4PY_SWIGPTR(Request    );
MPI4PY_SWIGPTR(Datatype   );
MPI4PY_SWIGPTR(Errhandler );


/*
 * Local Variables:
 * mode: C
 * End:
 */
