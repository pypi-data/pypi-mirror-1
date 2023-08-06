/* $Id: fastdefs.h 38 2007-07-12 15:51:17Z dalcinl $ */

#ifndef Py_MPI4PY_FASTDEFS_H
#define Py_MPI4PY_FASTDEFS_H

/* ---------------------------------------------------------------- */

#undef  MPI4PY_CALL_COMM_NEW
#define MPI4PY_CALL_COMM_NEW(COMM, NEWCOMM, COMM_NEW_CALL)	\
  do {								\
    int __ChkErr = MPI_SUCCESS;					\
    MPI4PY_RAISE_IF_NULL(COMM, MPI_COMM_NULL, MPI_ERR_COMM);	\
    MPI4PY_Py_BEGIN_ALLOW_THREADS				\
      __ChkErr = (COMM_NEW_CALL);				\
    MPI4PY_Py_END_ALLOW_THREADS					\
    if (__ChkErr != MPI_SUCCESS)				\
      MPI4PY_RAISE(__ChkErr);					\
    if ((NEWCOMM) != MPI_COMM_NULL)				\
      MPI4PY_COMM_SET_EH((NEWCOMM), MPI_ERRORS_RETURN);		\
  } while(0)

#undef  MPI4PY_CALL_WIN_NEW
#define MPI4PY_CALL_WIN_NEW(COMM, NEWWIN, WIN_NEW_CALL) \
  do {								\
    int __ChkErr = MPI_SUCCESS;					\
    MPI4PY_RAISE_IF_NULL(COMM, MPI_COMM_NULL, MPI_ERR_COMM);	\
    MPI4PY_Py_BEGIN_ALLOW_THREADS				\
      __ChkErr = (WIN_NEW_CALL);				\
    MPI4PY_Py_END_ALLOW_THREADS					\
    if (__ChkErr != MPI_SUCCESS)				\
      MPI4PY_RAISE(__ChkErr);					\
    if (NEWWIN != MPI_WIN_NULL)					\
      MPI4PY_WIN_SET_EH(NEWWIN, MPI_ERRORS_RETURN);		\
} while(0)

#undef  MPI4PY_CALL_FILE_NEW
#define MPI4PY_CALL_FILE_NEW(FILE, NEWFILE, FILE_NEW_CALL)	\
  do {								\
    int __ChkErr = MPI_SUCCESS;					\
    MPI4PY_Py_BEGIN_ALLOW_THREADS				\
      __ChkErr = (FILE_NEW_CALL);				\
    MPI4PY_Py_END_ALLOW_THREADS					\
    if (__ChkErr != MPI_SUCCESS)				\
      MPI4PY_RAISE(__ChkErr);					\
    if (NEWFILE != MPI_FILE_NULL)				\
      MPI4PY_FILE_SET_EH(NEWFILE, MPI_ERRORS_RETURN);		\
} while(0)

/* ---------------------------------------------------------------- */

#undef  MPI4PY_CALL
#define MPI4PY_CALL(MPI_CALL)					\
  do {								\
    int __ChkErr = MPI_SUCCESS;					\
    MPI4PY_Py_BEGIN_ALLOW_THREADS				\
      __ChkErr = (MPI_CALL);					\
    MPI4PY_Py_END_ALLOW_THREADS					\
    if (__ChkErr != MPI_SUCCESS)				\
      MPI4PY_RAISE(__ChkErr);					\
  } while(0)

#undef  MPI4PY_CALL_HANDLE
#define MPI4PY_CALL_HANDLE(HANDLE, HANDLE_CALL,			\
                           CHK_NULL, HDL_NULL, ERR_CLS,		\
                           GET_EH, SET_EH)			\
  do {								\
    int __ChkErr = MPI_SUCCESS;					\
    if (CHK_NULL)						\
      MPI4PY_RAISE_IF_NULL(HANDLE, HDL_NULL, ERR_CLS);		\
    MPI4PY_Py_BEGIN_ALLOW_THREADS				\
      __ChkErr = (HANDLE_CALL);					\
    MPI4PY_Py_END_ALLOW_THREADS					\
    if (__ChkErr != MPI_SUCCESS)				\
      MPI4PY_RAISE(__ChkErr);					\
  } while(0)


/* ---------------------------------------------------------------- */

#undef  MPI4PY_HANDLE_ENTER
#define MPI4PY_HANDLE_ENTER(Type, TYPE, HANDLE) \
  do {						\
    int __##TYPE##_IErr = MPI_SUCCESS;		\

#undef  MPI4PY_HANDLE_EXEC
#define MPI4PY_HANDLE_EXEC(Type, TYPE, HANDLE_CALL)	\
  do {							\
    __##TYPE##_IErr = (HANDLE_CALL);			\
    if (__##TYPE##_IErr != MPI_SUCCESS)			\
      goto __##TYPE##_fail;				\
  } while(0)

#undef  MPI4PY_HANDLE_EXIT
#define MPI4PY_HANDLE_EXIT(Type, TYPE, HANDLE)	\
  __##TYPE##_fail:				\
  if (__##TYPE##_IErr != MPI_SUCCESS)		\
    MPI4PY_RAISE(__##TYPE##_IErr);		\
  } while(0)

/* ---------------------------------------------------------------- */

#undef  MPI4PY_CALL_FREE
#define MPI4PY_CALL_FREE(FREE_CALL)				\
  do {								\
    int __ChkErr = MPI_SUCCESS;					\
    __ChkErr = (FREE_CALL);					\
    if (__ChkErr != MPI_SUCCESS) MPI4PY_RAISE(__ChkErr);	\
  } while(0)


#undef  MPI4PY_CALL_HANDLE_FREE
#define MPI4PY_CALL_HANDLE_FREE(HANDLE, HANDLE_FREE_CALL,	     \
                                CHK_NULL, HDL_NULL, ERR_CLS,	     \
                                GET_EH, SET_EH)			     \
  do {								     \
    int __ChkErr = MPI_SUCCESS;					     \
    if (CHK_NULL)						     \
      MPI4PY_RAISE_IF_NULL(HANDLE, HDL_NULL, ERR_CLS);		     \
    __ChkErr = (HANDLE_FREE_CALL);				     \
    if (__ChkErr != MPI_SUCCESS)				     \
      MPI4PY_RAISE(__ChkErr);					     \
  } while(0)

/* ---------------------------------------------------------------- */

#endif /* !Py_MPI4PY_FASTDEFS_H */
