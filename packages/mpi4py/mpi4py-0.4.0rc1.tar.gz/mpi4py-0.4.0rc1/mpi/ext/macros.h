/* $Id: macros.h,v 1.19 2006/10/09 17:03:51 dalcinl Exp $ */

#ifndef Py_MPI4PY_MACROS_H
#define Py_MPI4PY_MACROS_H

/* ---------------------------------------------------------------- */

#define TRY
#define RAISE  goto fail
#define EXCEPT fail:

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */

#define MPI4PY_RAISE_MPINOIMPL(FEATURE) do { \
  PyErr_SetString(PyExc_NotImplementedError, FEATURE " " \
		  "unavailable in this MPI implementation"); RAISE; \
} while(0)

#define MPI4PY_WARN_MPINOIMPL(FEATURE, MESSAGE) do { \
  if (PyErr_Warn(PyExc_MPIWarning, FEATURE " " \
                 "unavailable in this MPI implementation" \
                 ", " MESSAGE) < 0) RAISE; \
} while(0)

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */

#define PY_RAISE(PYEXC, MESSAGE) do { \
  PyErr_SetString((PYEXC), (MESSAGE)); RAISE; \
} while(0)


#define MPI4PY_SET_ERROR(IERR) do { \
  PyObject *__oierr = PyInt_FromLong((long)(IERR)); \
  PyErr_SetObject(PyExc_MPIError, __oierr); \
   Py_XDECREF(__oierr); \
} while (0)

#define MPI4PY_RAISE(IERR) \
do { MPI4PY_SET_ERROR(IERR); RAISE; } while(0)

#define MPI4PY_CHECK_NOT_EQ(HANDLE1, HANDLE2, ERR_HANDLE) do { \
 if ((HANDLE1) == (HANDLE2)) MPI4PY_RAISE(ERR_HANDLE); \
} while(0)

#define MPI4PY_CHECK_NULL(HANDLE, HANDLE_NULL, ERR_HANDLE) \
if ( (HANDLE) == (HANDLE_NULL) ) \
  { MPI4PY_SET_ERROR(ERR_HANDLE); return NULL; }          


#define MPI4PY_CHECK(IERR) do { \
  int _ChkErr_ = (IERR); \
  if (_ChkErr_ != MPI_SUCCESS) MPI4PY_RAISE(_ChkErr_); \
} while (0)


/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */

#define MPI4PY_RAISE_IF_NULL(HANDLE, HANDLE_NULL, ERR_HANDLE) do { \
  if ((HANDLE) == (HANDLE_NULL)) MPI4PY_RAISE(ERR_HANDLE); \
} while(0)


#define MPI4PY_FREE_EH(EH) do {       \
  if ((EH) != MPI_ERRORS_ARE_FATAL && \
      (EH) != MPI_ERRORS_RETURN)      \
    MPI_Errhandler_free(&(EH));       \
  else                                \
    (EH) = MPI_ERRHANDLER_NULL;       \
} while(0)

/* Hack for MPICH !!! */
#if defined(MPICH_NAME)
#undef  MPI4PY_FREE_EH
#define MPI4PY_FREE_EH(EH) do { \
  MPI_Errhandler_free(&(EH));   \
} while(0)
#endif

/* Hack for LAM !!! */
#if defined(LAM_MPI)
struct _errhdl {
  void  (*eh_func)(void);
  int   eh_refcount;
  int   eh_f77handle;
  int   eh_flags;
};
#undef  MPI4PY_FREE_EH
#define MPI4PY_FREE_EH(EH) do {     \
  if (EH != MPI_ERRORS_ARE_FATAL && \
      EH != MPI_ERRORS_RETURN)      \
    MPI_Errhandler_free(&(EH));     \
  else {                            \
    (EH)->eh_refcount--;            \
    (EH) = MPI_ERRHANDLER_NULL;     \
  }                                 \
} while(0)
#endif

/* ---------------------------------------------------------------- */

#define MPI4PY_CALL_COMM_NEW(COMM, NEWCOMM, COMM_NEW_CALL) do { \
  int __ChkErr; MPI_Errhandler __ErrHdl = MPI_ERRHANDLER_NULL; \
  MPI4PY_RAISE_IF_NULL(COMM, MPI_COMM_NULL, MPI_ERR_COMM); \
  MPI_Errhandler_get((COMM), &__ErrHdl); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set((COMM), MPI_ERRORS_RETURN); \
  Py_BEGIN_ALLOW_THREADS \
  __ChkErr = (COMM_NEW_CALL); \
  Py_END_ALLOW_THREADS \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set((COMM), __ErrHdl); \
  if (__ChkErr != MPI_SUCCESS) \
    { MPI4PY_FREE_EH(__ErrHdl); MPI4PY_RAISE(__ChkErr); } \
  if ((NEWCOMM) != MPI_COMM_NULL) \
     if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
       MPI_Errhandler_set((NEWCOMM), __ErrHdl); \
  MPI4PY_FREE_EH(__ErrHdl); \
} while(0)

#define MPI4PY_CALL_WIN_NEW(COMM, NEWWIN, WIN_NEW_CALL) do { \
  int __ChkErr; MPI_Errhandler __ErrHdl = MPI_ERRHANDLER_NULL; \
  MPI4PY_RAISE_IF_NULL(COMM, MPI_COMM_NULL, MPI_ERR_COMM); \
  MPI_Errhandler_get((COMM), &__ErrHdl); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set((COMM), MPI_ERRORS_RETURN); \
  Py_BEGIN_ALLOW_THREADS \
  __ChkErr = (WIN_NEW_CALL); \
  Py_END_ALLOW_THREADS \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set((COMM), __ErrHdl); \
  if (__ChkErr != MPI_SUCCESS) \
    { MPI4PY_FREE_EH(__ErrHdl); MPI4PY_RAISE(__ChkErr); } \
  if (NEWWIN != MPI_WIN_NULL) \
     if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
       MPI_Win_set_errhandler(NEWWIN, __ErrHdl); \
  MPI4PY_FREE_EH(__ErrHdl); \
} while(0)

#define MPI4PY_CALL_FILE_NEW(FILE, NEWFILE, FILE_NEW_CALL) do { \
  int __ChkErr; MPI_Errhandler __ErrHdl = MPI_ERRHANDLER_NULL; \
  MPI_File_get_errhandler((FILE), &__ErrHdl); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_File_set_errhandler((FILE), MPI_ERRORS_RETURN); \
  Py_BEGIN_ALLOW_THREADS \
  __ChkErr = (FILE_NEW_CALL); \
  Py_END_ALLOW_THREADS \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_File_set_errhandler((FILE), __ErrHdl); \
  if (__ChkErr != MPI_SUCCESS) \
    { MPI4PY_FREE_EH(__ErrHdl); MPI4PY_RAISE(__ChkErr); } \
  if (NEWFILE != MPI_FILE_NULL) \
     if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
       MPI_File_set_errhandler(NEWFILE, __ErrHdl); \
  MPI4PY_FREE_EH(__ErrHdl); \
} while(0)

/* ---------------------------------------------------------------- */

#define MPI4PY_CALL(MPI_CALL) do { \
  int __ChkErr; MPI_Errhandler __ErrHdl = MPI_ERRHANDLER_NULL; \
  MPI_Errhandler_get(MPI_COMM_WORLD, &__ErrHdl); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set(MPI_COMM_WORLD, MPI_ERRORS_RETURN); \
  Py_BEGIN_ALLOW_THREADS \
  __ChkErr = (MPI_CALL); \
  Py_END_ALLOW_THREADS \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set(MPI_COMM_WORLD, __ErrHdl); \
  MPI4PY_FREE_EH(__ErrHdl); \
  if (__ChkErr != MPI_SUCCESS) MPI4PY_RAISE(__ChkErr); \
} while(0)

#define MPI4PY_CALL_HANDLE(HANDLE, HANDLE_CALL, \
                           CHECK_NULL, HANDLE_NULL, ERR_HANDLE, \
                           GET_EH, SET_EH) do { \
  int __ChkErr; MPI_Errhandler __ErrHdl = MPI_ERRHANDLER_NULL; \
  if (CHECK_NULL) \
     MPI4PY_RAISE_IF_NULL(HANDLE, HANDLE_NULL, ERR_HANDLE); \
  GET_EH((HANDLE), &__ErrHdl); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     SET_EH((HANDLE), MPI_ERRORS_RETURN); \
  Py_BEGIN_ALLOW_THREADS \
  __ChkErr = (HANDLE_CALL); \
  Py_END_ALLOW_THREADS \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     SET_EH((HANDLE), __ErrHdl); \
  MPI4PY_FREE_EH(__ErrHdl); \
  if (__ChkErr != MPI_SUCCESS) MPI4PY_RAISE(__ChkErr); \
} while(0)

#define MPI4PY_CALL_COMM(COMM, COMM_CALL) \
        MPI4PY_CALL_HANDLE(COMM, COMM_CALL, \
                           1, MPI_COMM_NULL, MPI_ERR_COMM, \
                           MPI_Errhandler_get, MPI_Errhandler_set)

#define MPI4PY_CALL_COMM_WORLD(COMM_CALL) \
        MPI4PY_CALL_HANDLE(MPI_COMM_WORLD, COMM_CALL, \
                           1, MPI_COMM_NULL, MPI_ERR_COMM, \
                           MPI_Errhandler_get, MPI_Errhandler_set)

#define MPI4PY_CALL_WIN(WIN, WIN_CALL) \
        MPI4PY_CALL_HANDLE(WIN, WIN_CALL, \
                           1, MPI_WIN_NULL, MPI_ERR_WIN, \
                           MPI_Win_get_errhandler, MPI_Win_set_errhandler)

#define MPI4PY_CALL_FILE(FILE, FILE_CALL) \
        MPI4PY_CALL_HANDLE(FILE, FILE_CALL, \
                           1, MPI_FILE_NULL, MPI_ERR_FILE, \
                           MPI_File_get_errhandler, MPI_File_set_errhandler)

#define MPI4PY_CALL_FILE_NULL(FILE_CALL) \
        MPI4PY_CALL_HANDLE(MPI_FILE_NULL, FILE_CALL, \
                           0, MPI_FILE_NULL, MPI_ERR_FILE, \
                           MPI_File_get_errhandler, MPI_File_set_errhandler)

/* ---------------------------------------------------------------- */

#define MPI4PY_CALL_FREE(FREE_CALL) do { \
  int __ChkErr; MPI_Errhandler __ErrHdl = MPI_ERRHANDLER_NULL; \
  MPI_Errhandler_get(MPI_COMM_WORLD, &__ErrHdl); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set(MPI_COMM_WORLD, MPI_ERRORS_RETURN); \
  __ChkErr = (FREE_CALL); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     MPI_Errhandler_set(MPI_COMM_WORLD, __ErrHdl); \
  MPI4PY_FREE_EH(__ErrHdl); \
  if (__ChkErr != MPI_SUCCESS) MPI4PY_RAISE(__ChkErr); \
} while(0)

#define MPI4PY_CALL_HANDLE_FREE(HANDLE, HANDLE_FREE_CALL, \
                                CHECK_NULL, HANDLE_NULL, ERR_HANDLE, \
                                GET_EH, SET_EH) do { \
  int __ChkErr; MPI_Errhandler __ErrHdl = MPI_ERRHANDLER_NULL; \
  if (CHECK_NULL) \
     MPI4PY_RAISE_IF_NULL(HANDLE, HANDLE_NULL, ERR_HANDLE); \
  GET_EH((HANDLE), &__ErrHdl); \
  if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
     SET_EH((HANDLE), MPI_ERRORS_RETURN); \
  __ChkErr = (HANDLE_FREE_CALL); \
  if ((HANDLE) != (HANDLE_NULL)) \
     if (__ErrHdl == MPI_ERRORS_ARE_FATAL) \
        SET_EH((HANDLE), __ErrHdl); \
  MPI4PY_FREE_EH(__ErrHdl); \
  if (__ChkErr != MPI_SUCCESS) MPI4PY_RAISE(__ChkErr); \
} while(0)

#define MPI4PY_CALL_COMM_FREE(COMM, COMM_FREE_CALL) \
        MPI4PY_CALL_HANDLE_FREE(COMM, COMM_FREE_CALL, \
                                1, MPI_COMM_NULL, MPI_ERR_COMM, \
                                MPI_Errhandler_get, MPI_Errhandler_set)

#define MPI4PY_CALL_WIN_FREE(WIN, WIN_FREE_CALL) \
        MPI4PY_CALL_HANDLE_FREE(WIN, WIN_FREE_CALL, \
                                1, MPI_WIN_NULL, MPI_ERR_WIN, \
                                MPI_Win_get_errhandler, MPI_Win_set_errhandler)

#define MPI4PY_CALL_FILE_FREE(FILE, FILE_FREE_CALL) \
        MPI4PY_CALL_HANDLE_FREE(FILE, FILE_FREE_CALL, \
                                1, MPI_FILE_NULL, MPI_ERR_FILE, \
                                MPI_File_get_errhandler, MPI_File_set_errhandler)

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* Open MPI 1.1.1 - MPI_File_get_errhandler is broken               */
/* ---------------------------------------------------------------- */
#if defined(OPEN_MPI)
static MPI_Errhandler OMPI_FILE_NULL_ERRHANDLER = (MPI_Errhandler)0;
static int OMPI_File_get_errhandler(MPI_File file, MPI_Errhandler *errhandler)
{
  if (file == MPI_FILE_NULL) {
    if (OMPI_FILE_NULL_ERRHANDLER == (MPI_Errhandler)0)
      OMPI_FILE_NULL_ERRHANDLER = MPI_ERRORS_RETURN;
    *errhandler = OMPI_FILE_NULL_ERRHANDLER;
    return MPI_SUCCESS;
  }
  return MPI_File_get_errhandler(file, errhandler);
}
static int OMPI_File_set_errhandler(MPI_File file, MPI_Errhandler errhandler)
{
  int ierr = MPI_File_set_errhandler(file, errhandler);
  if (file == MPI_FILE_NULL && ierr == MPI_SUCCESS) {
    OMPI_FILE_NULL_ERRHANDLER = errhandler;
  }
  return ierr;
}
#define MPI_File_get_errhandler(file, errhdl) \
        OMPI_File_get_errhandler((file),(errhdl))
#define MPI_File_set_errhandler(file, errhdl) \
        OMPI_File_set_errhandler((file),(errhdl))
#endif

/* ---------------------------------------------------------------- */


#endif /* !Py_MPI4PY_MACROS_H */
