/* $Id: compat.h 165 2008-02-04 21:29:08Z dalcinl $ */

#ifndef Py_MPI4PY_COMPAT_H
#define Py_MPI4PY_COMPAT_H

/*------------------------------------------------------------------*/

#if !HAVE_MPI_LONG_LONG
#if !defined(MPI_LONG_LONG)
#define MPI_LONG_LONG MPI_DATATYPE_NULL
#endif
#endif

#if !HAVE_MPI_LONG_LONG_INT
#if !defined(MPI_LONG_LONG_INT)
#define MPI_LONG_LONG_INT MPI_DATATYPE_NULL
#endif
#endif

#if !HAVE_MPI_UNSIGNED_LONG_LONG
#if !defined(MPI_UNSIGNED_LONG_LONG)
#define MPI_UNSIGNED_LONG_LONG MPI_DATATYPE_NULL
#endif
#endif

#if !HAVE_MPI_SIGNED_CHAR
#if !defined(MPI_SIGNED_CHAR)
#define MPI_SIGNED_CHAR MPI_DATATYPE_NULL
#endif
#endif

#if !HAVE_MPI_WCHAR
#if !defined(MPI_WCHAR)
#define MPI_WCHAR MPI_DATATYPE_NULL
#endif
#endif

#if !HAVE_MPI_TYPE_CREATE_SUBARRAY
#if !defined(MPI_ORDER_C)
#define MPI_ORDER_C 0
#endif
#if !defined(MPI_ORDER_FORTRAN)
#define MPI_ORDER_FORTRAN 1
#endif
#endif

#if !HAVE_MPI_TYPE_CREATE_DARRAY
#if !defined(MPI_DISTRIBUTE_NONE)
#define MPI_DISTRIBUTE_NONE MPI_UNDEFINED
#endif
#if !defined(MPI_DISTRIBUTE_BLOCK)
#define MPI_DISTRIBUTE_BLOCK MPI_UNDEFINED
#endif
#if !defined(MPI_DISTRIBUTE_CYCLIC)
#define MPI_DISTRIBUTE_CYCLIC MPI_UNDEFINED
#endif
#if !defined(MPI_DISTRIBUTE_DFLT_DARG)
#define MPI_DISTRIBUTE_DFLT_DARG MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_TYPE_MATCH_SIZE
#if !defined(MPI_TYPECLASS_INTEGER)
#define MPI_TYPECLASS_INTEGER MPI_UNDEFINED
#endif
#if !defined(MPI_TYPECLASS_REAL)
#define MPI_TYPECLASS_REAL MPI_UNDEFINED
#endif
#if !defined(MPI_TYPECLASS_COMPLEX)
#define MPI_TYPECLASS_COMPLEX MPI_UNDEFINED
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_IN_PLACE
#if !defined(MPI_IN_PLACE)
#define MPI_IN_PLACE (void *)MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_ROOT
#if !defined(MPI_ROOT)
#define MPI_ROOT MPI_UNDEFINED
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_INFO_NULL
#if !defined(MPI_INFO_NULL)
#if !defined(MPI_Info)
#define MPI_Info void*
#endif
#define MPI_INFO_NULL ((MPI_Info)0)
#endif
#endif

#if !HAVE_MPI_ERR_INFO
#if !defined(MPI_ERR_INFO)
#define MPI_ERR_INFO MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_INFO_KEY
#if !defined(MPI_ERR_INFO_KEY)
#define MPI_ERR_INFO_KEY MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_INFO_VAL
#if !defined(MPI_ERR_INFO_VAL)
#define MPI_ERR_INFO_VAL MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_INFO_NOKEY
#if !defined(MPI_ERR_INFO_NOKEY)
#define MPI_ERR_INFO_NOKEY MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_INFO_NULL
#if !defined(MPI_MAX_INFO_KEY)
#define MPI_MAX_INFO_KEY 0
#endif
#endif

#if !HAVE_MPI_INFO_NULL
#if !defined(MPI_MAX_INFO_VAL)
#define MPI_MAX_INFO_VAL 0
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_WIN_NULL
#if !defined(MPI_WIN_NULL)
#if !defined(MPI_Win)
#define MPI_Win void*
#endif
#define MPI_WIN_NULL ((MPI_Win)0)
#endif
#endif

#if !HAVE_MPI_MODE_NOCHECK
#if !defined(MPI_MODE_NOCHECK)
#define MPI_MODE_NOCHECK MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_NOSTORE
#if !defined(MPI_MODE_NOSTORE)
#define MPI_MODE_NOSTORE MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_NOPUT
#if !defined(MPI_MODE_NOPUT)
#define MPI_MODE_NOPUT MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_NOPRECEDE
#if !defined(MPI_MODE_NOPRECEDE)
#define MPI_MODE_NOPRECEDE MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_NOSUCCEED
#if !defined(MPI_MODE_NOSUCCEED)
#define MPI_MODE_NOSUCCEED MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_LOCK_EXCLUSIVE
#if !defined(MPI_LOCK_EXCLUSIVE)
#define MPI_LOCK_EXCLUSIVE MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_LOCK_SHARED
#if !defined(MPI_LOCK_SHARED)
#define MPI_LOCK_SHARED MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_ERR_WIN
#if !defined(MPI_ERR_WIN)
#define MPI_ERR_WIN MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_BASE
#if !defined(MPI_ERR_BASE)
#define MPI_ERR_BASE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_SIZE
#if !defined(MPI_ERR_SIZE)
#define MPI_ERR_SIZE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_DISP
#if !defined(MPI_ERR_DISP)
#define MPI_ERR_DISP MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_LOCKTYPE
#if !defined(MPI_ERR_LOCKTYPE)
#define MPI_ERR_LOCKTYPE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_ASSERT
#if !defined(MPI_ERR_ASSERT)
#define MPI_ERR_ASSERT MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_ASSERT
#if !defined(MPI_ERR_ASSERT)
#define MPI_ERR_ASSERT MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_RMA_CONFLICT
#if !defined(MPI_ERR_RMA_CONFLICT)
#define MPI_ERR_RMA_CONFLICT MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_RMA_SYNC
#if !defined(MPI_ERR_RMA_SYNC)
#define MPI_ERR_RMA_SYNC MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_REPLACE
#if !defined(MPI_REPLACE)
#define MPI_REPLACE MPI_OP_NULL
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_FILE_NULL
#if !defined(MPI_FILE_NULL)
#if !defined(MPI_File)
#define MPI_File void*
#endif
#define MPI_FILE_NULL ((MPI_File)0)
#endif
#endif

#if !HAVE_MPI_DISPLACEMENT_CURRENT
#if !defined(MPI_DISPLACEMENT_CURRENT)
#define MPI_DISPLACEMENT_CURRENT MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_RDONLY
#if !defined(MPI_MODE_RDONLY)
#define MPI_MODE_RDONLY MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_RDWR
#if !defined(MPI_MODE_RDWR)
#define MPI_MODE_RDWR MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_WRONLY
#if !defined(MPI_MODE_WRONLY)
#define MPI_MODE_WRONLY MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_CREATE
#if !defined(MPI_MODE_CREATE)
#define MPI_MODE_CREATE MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_EXCL
#if !defined(MPI_MODE_EXCL)
#define MPI_MODE_EXCL MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_DELETE_ON_CLOSE
#if !defined(MPI_MODE_DELETE_ON_CLOSE)
#define MPI_MODE_DELETE_ON_CLOSE MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_UNIQUE_OPEN
#if !defined(MPI_MODE_UNIQUE_OPEN)
#define MPI_MODE_UNIQUE_OPEN MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_SEQUENTIAL
#if !defined(MPI_MODE_SEQUENTIAL)
#define MPI_MODE_SEQUENTIAL MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_MODE_APPEND
#if !defined(MPI_MODE_APPEND)
#define MPI_MODE_APPEND MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_SEEK_SET
#if !defined(MPI_SEEK_SET)
#define MPI_SEEK_SET MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_SEEK_CUR
#if !defined(MPI_SEEK_CUR)
#define MPI_SEEK_CUR MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_SEEK_END
#if !defined(MPI_SEEK_END)
#define MPI_SEEK_END MPI_UNDEFINED
#endif
#endif

#if !HAVE_MPI_ERR_FILE
#if !defined(MPI_ERR_FILE)
#define MPI_ERR_FILE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_NOT_SAME
#if !defined(MPI_ERR_NOT_SAME)
#define MPI_ERR_NOT_SAME MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_AMODE
#if !defined(MPI_ERR_AMODE)
#define MPI_ERR_AMODE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_UNSUPPORTED_DATAREP
#if !defined(MPI_ERR_UNSUPPORTED_DATAREP)
#define MPI_ERR_UNSUPPORTED_DATAREP MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_UNSUPPORTED_OPERATION
#if !defined(MPI_ERR_UNSUPPORTED_OPERATION)
#define MPI_ERR_UNSUPPORTED_OPERATION MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_NO_SUCH_FILE
#if !defined(MPI_ERR_NO_SUCH_FILE)
#define MPI_ERR_NO_SUCH_FILE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_FILE_EXISTS
#if !defined(MPI_ERR_FILE_EXISTS)
#define MPI_ERR_FILE_EXISTS MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_BAD_FILE
#if !defined(MPI_ERR_BAD_FILE)
#define MPI_ERR_BAD_FILE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_ACCESS
#if !defined(MPI_ERR_ACCESS)
#define MPI_ERR_ACCESS MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_NO_SPACE
#if !defined(MPI_ERR_NO_SPACE)
#define MPI_ERR_NO_SPACE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_QUOTA
#if !defined(MPI_ERR_QUOTA)
#define MPI_ERR_QUOTA MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_READ_ONLY
#if !defined(MPI_ERR_READ_ONLY)
#define MPI_ERR_READ_ONLY MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_FILE_IN_USE
#if !defined(MPI_ERR_FILE_IN_USE)
#define MPI_ERR_FILE_IN_USE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_DUP_DATAREP
#if !defined(MPI_ERR_DUP_DATAREP)
#define MPI_ERR_DUP_DATAREP MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_CONVERSION
#if !defined(MPI_ERR_CONVERSION)
#define MPI_ERR_CONVERSION MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_IO
#if !defined(MPI_ERR_IO)
#define MPI_ERR_IO MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_MAX_DATAREP_STRING
#if !defined(MPI_MAX_DATAREP_STRING)
#define MPI_MAX_DATAREP_STRING 0
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_ERR_NO_MEM
#if !defined(MPI_ERR_NO_MEM)
#define MPI_ERR_NO_MEM MPI_ERR_OTHER
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_ERR_NAME
#if !defined(MPI_ERR_NAME)
#define MPI_ERR_NAME MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_PORT
#if !defined(MPI_ERR_PORT)
#define MPI_ERR_PORT MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_SERVICE
#if !defined(MPI_ERR_SERVICE)
#define MPI_ERR_SERVICE MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_ERR_SPAWN
#if !defined(MPI_ERR_SPAWN)
#define MPI_ERR_SPAWN MPI_ERR_OTHER
#endif
#endif

#if !HAVE_MPI_OPEN_PORT && !HAVE_MPI_LOOKUP_NAME
#if !defined(MPI_MAX_PORT_NAME)
#define MPI_MAX_PORT_NAME 0
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_MAX_OBJECT_NAME
#if !defined(MPI_MAX_OBJECT_NAME)
#define MPI_MAX_OBJECT_NAME 0
#endif
#endif

/*------------------------------------------------------------------*/

#if !HAVE_MPI_ERR_KEYVAL
#if !defined(MPI_ERR_KEYVAL)
#define MPI_ERR_KEYVAL MPI_ERR_OTHER
#endif
#endif

/*------------------------------------------------------------------*/



/*------------------------------------------------------------------*/

#if (defined(MPICH_NAME) && MPICH_NAME == 1)
#undef  HAVE_MPI_STATUS_IGNORE
#define HAVE_MPI_STATUS_IGNORE 0
#undef  HAVE_MPI_STATUSES_IGNORE
#define HAVE_MPI_STATUSES_IGNORE 0
#endif

#if (defined(MPICH_NAME) && MPICH_NAME == 1)
#undef  HAVE_MPI_ROOT
#define HAVE_MPI_ROOT 0
#endif

#if (defined(MPICH_NAME) && MPICH_NAME == 1)
#undef  HAVE_MPI_MAX_OBJECT_NAME
#define HAVE_MPI_MAX_OBJECT_NAME 1
#if !defined(MPI_MAX_OBJECT_NAME)
#define MPI_MAX_OBJECT_NAME MPI_MAX_NAME_STRING
#endif
#endif

/*------------------------------------------------------------------*/

#if defined(LAM_MPI)
#undef  HAVE_MPI_WIN_TEST
#define HAVE_MPI_WIN_TEST 0
#undef  HAVE_MPI_WIN_LOCK
#define HAVE_MPI_WIN_LOCK 0
#undef  HAVE_MPI_WIN_UNLOCK
#define HAVE_MPI_WIN_UNLOCK 0
#endif

/*------------------------------------------------------------------*/


#endif /* !Py_MPI4PY_COMPAT_H */
