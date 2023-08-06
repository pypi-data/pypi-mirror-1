/* $Id: config.h 165 2008-02-04 21:29:08Z dalcinl $ */

#ifndef Py_MPI4PY_CONFIG_H
#define Py_MPI4PY_CONFIG_H

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_VERSION
#if defined(MPI_VERSION)
#define HAVE_MPI_VERSION 1
#else
#define HAVE_MPI_VERSION 0
#endif
#endif

#ifndef HAVE_MPI_2
#if defined(MPI_VERSION) && (MPI_VERSION >= 2)
#define HAVE_MPI_2 1
#else
#define HAVE_MPI_2 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_GET_VERSION
#if HAVE_MPI_VERSION
#define HAVE_MPI_GET_VERSION 1
#else
#define HAVE_MPI_GET_VERSION 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_INIT_THREAD
#if HAVE_MPI_2
#define HAVE_MPI_INIT_THREAD 1
#else
#define HAVE_MPI_INIT_THREAD 0
#endif
#endif

#ifndef HAVE_MPI_QUERY_THREAD
#if HAVE_MPI_2
#define HAVE_MPI_QUERY_THREAD 1
#else
#define HAVE_MPI_QUERY_THREAD 0
#endif
#endif

#ifndef HAVE_MPI_IS_THREAD_MAIN
#if HAVE_MPI_2
#define HAVE_MPI_IS_THREAD_MAIN 1
#else
#define HAVE_MPI_IS_THREAD_MAIN 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_WCHAR
#if HAVE_MPI_2
#define HAVE_MPI_WCHAR 1
#else
#define HAVE_MPI_WCHAR 0
#endif
#endif

#ifndef HAVE_MPI_SIGNED_CHAR
#if HAVE_MPI_2
#define HAVE_MPI_SIGNED_CHAR 1
#else
#define HAVE_MPI_SIGNED_CHAR 0
#endif
#endif

#ifndef HAVE_MPI_LONG_LONG
#if HAVE_LONG_LONG
#define HAVE_MPI_LONG_LONG 1
#else
#define HAVE_MPI_LONG_LONG 0
#endif
#endif

#ifndef HAVE_MPI_LONG_LONG_INT
#if HAVE_LONG_LONG
#define HAVE_MPI_LONG_LONG_INT 1
#else
#define HAVE_MPI_LONG_LONG_INT 0
#endif
#endif

#ifndef HAVE_MPI_UNSIGNED_LONG_LONG
#if HAVE_LONG_LONG && HAVE_MPI_2
#define HAVE_MPI_UNSIGNED_LONG_LONG 1
#else
#define HAVE_MPI_UNSIGNED_LONG_LONG 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_GET_EXTENT
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_GET_EXTENT 1
#else
#define HAVE_MPI_TYPE_GET_EXTENT 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_DUP
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_DUP 1
#else
#define HAVE_MPI_TYPE_DUP 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_CREATE_INDEXED_BLOCK
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_CREATE_INDEXED_BLOCK 1
#else
#define HAVE_MPI_TYPE_CREATE_INDEXED_BLOCK 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_CREATE_HVECTOR
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_CREATE_HVECTOR 1
#else
#define HAVE_MPI_TYPE_CREATE_HVECTOR 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_CREATE_HINDEXED
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_CREATE_HINDEXED 1
#else
#define HAVE_MPI_TYPE_CREATE_HINDEXED 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_CREATE_SUBARRAY
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_CREATE_SUBARRAY 1
#else
#define HAVE_MPI_TYPE_CREATE_SUBARRAY 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_CREATE_DARRAY
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_CREATE_DARRAY 1
#else
#define HAVE_MPI_TYPE_CREATE_DARRAY 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_CREATE_STRUCT
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_CREATE_STRUCT 1
#else
#define HAVE_MPI_TYPE_CREATE_STRUCT 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_MATCH_SIZE
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_MATCH_SIZE 1
#else
#define HAVE_MPI_TYPE_MATCH_SIZE 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_CREATE_RESIZED
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_CREATE_RESIZED 1
#else
#define HAVE_MPI_TYPE_CREATE_RESIZED 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_GET_TRUE_EXTENT
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_GET_TRUE_EXTENT 1
#else
#define HAVE_MPI_TYPE_GET_TRUE_EXTENT 0
#endif
#endif

#ifndef HAVE_MPI_GET_ADDRESS
#if HAVE_MPI_2
#define HAVE_MPI_GET_ADDRESS 1
#else
#define HAVE_MPI_GET_ADDRESS 0
#endif
#endif

#ifndef HAVE_MPI_PACK_EXTERNAL
#if HAVE_MPI_2
#define HAVE_MPI_PACK_EXTERNAL 1
#else
#define HAVE_MPI_PACK_EXTERNAL 0
#endif
#endif

#ifndef HAVE_MPI_UNPACK_EXTERNAL
#if HAVE_MPI_2
#define HAVE_MPI_UNPACK_EXTERNAL 1
#else
#define HAVE_MPI_UNPACK_EXTERNAL 0
#endif
#endif

#ifndef HAVE_MPI_PACK_EXTERNAL_SIZE
#if HAVE_MPI_2
#define HAVE_MPI_PACK_EXTERNAL_SIZE 1
#else
#define HAVE_MPI_PACK_EXTERNAL_SIZE 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_STATUS_IGNORE
#if HAVE_MPI_2
#define HAVE_MPI_STATUS_IGNORE 1
#else
#define HAVE_MPI_STATUS_IGNORE 0
#endif
#endif

#ifndef HAVE_MPI_STATUSES_IGNORE
#if HAVE_MPI_2
#define HAVE_MPI_STATUSES_IGNORE 1
#else
#define HAVE_MPI_STATUSES_IGNORE 0
#endif
#endif

#ifndef HAVE_MPI_STATUS_SET_ELEMENTS
#if HAVE_MPI_2
#define HAVE_MPI_STATUS_SET_ELEMENTS 1
#else
#define HAVE_MPI_STATUS_SET_ELEMENTS 0
#endif
#endif

#ifndef HAVE_MPI_STATUS_SET_CANCELLED
#if HAVE_MPI_2
#define HAVE_MPI_STATUS_SET_CANCELLED 1
#else
#define HAVE_MPI_STATUS_SET_CANCELLED 0
#endif
#endif

#ifndef HAVE_MPI_REQUEST_GET_STATUS
#if HAVE_MPI_2
#define HAVE_MPI_REQUEST_GET_STATUS 1
#else
#define HAVE_MPI_REQUEST_GET_STATUS 0
#endif
#endif

#ifndef HAVE_MPI_GREQUEST_START
#if HAVE_MPI_2
#define HAVE_MPI_GREQUEST_START 1
#else
#define HAVE_MPI_GREQUEST_START 0
#endif
#endif

#ifndef HAVE_MPI_GREQUEST_COMPLETE
#if HAVE_MPI_2
#define HAVE_MPI_GREQUEST_COMPLETE 1
#else
#define HAVE_MPI_GREQUEST_COMPLETE 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_IN_PLACE
#if HAVE_MPI_2
#define HAVE_MPI_IN_PLACE 1
#else
#define HAVE_MPI_IN_PLACE 0
#endif
#endif

#ifndef HAVE_MPI_ROOT
#if HAVE_MPI_2
#define HAVE_MPI_ROOT 1
#else
#define HAVE_MPI_ROOT 0
#endif
#endif

#ifndef HAVE_MPI_EXSCAN
#if HAVE_MPI_2
#define HAVE_MPI_EXSCAN 1
#else
#define HAVE_MPI_EXSCAN 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_COMM_GET_ERRHANDLER
#if HAVE_MPI_2
#define HAVE_MPI_COMM_GET_ERRHANDLER 1
#else
#define HAVE_MPI_COMM_GET_ERRHANDLER 0
#endif
#endif

#ifndef HAVE_MPI_COMM_SET_ERRHANDLER
#if HAVE_MPI_2
#define HAVE_MPI_COMM_SET_ERRHANDLER 1
#else
#define HAVE_MPI_COMM_SET_ERRHANDLER 0
#endif
#endif

#ifndef HAVE_MPI_COMM_CALL_ERRHANDLER
#if HAVE_MPI_2
#define HAVE_MPI_COMM_CALL_ERRHANDLER 1
#else
#define HAVE_MPI_COMM_CALL_ERRHANDLER 0
#endif
#endif

#ifndef HAVE_MPI_UNIVERSE_SIZE
#if HAVE_MPI_2
#define HAVE_MPI_UNIVERSE_SIZE 1
#else
#define HAVE_MPI_UNIVERSE_SIZE 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_INFO_NULL
#if HAVE_MPI_2 || defined(MPI_INFO_NULL)
#define HAVE_MPI_INFO_NULL 1
#else
#define HAVE_MPI_INFO_NULL 0
#endif
#endif

#ifndef HAVE_MPI_INFO_CREATE
#if HAVE_MPI_2
#define HAVE_MPI_INFO_CREATE 1
#else
#define HAVE_MPI_INFO_CREATE 0
#endif
#endif

#ifndef HAVE_MPI_INFO_FREE
#if HAVE_MPI_2
#define HAVE_MPI_INFO_FREE 1
#else
#define HAVE_MPI_INFO_FREE 0
#endif
#endif

#ifndef HAVE_MPI_ERR_INFO
#if HAVE_MPI_2
#define HAVE_MPI_ERR_INFO 1
#else
#define HAVE_MPI_ERR_INFO 0
#endif
#endif

#ifndef HAVE_MPI_ERR_INFO_KEY
#if HAVE_MPI_2
#define HAVE_MPI_ERR_INFO_KEY 1
#else
#define HAVE_MPI_ERR_INFO_KEY 0
#endif
#endif

#ifndef HAVE_MPI_ERR_INFO_VALUE
#if HAVE_MPI_2
#define HAVE_MPI_ERR_INFO_VALUE 1
#else
#define HAVE_MPI_ERR_INFO_VALUE 0
#endif
#endif

#ifndef HAVE_MPI_ERR_INFO_NOKEY
#if HAVE_MPI_2
#define HAVE_MPI_ERR_INFO_NOKEY 1
#else
#define HAVE_MPI_ERR_INFO_NOKEY 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_WIN_NULL
#if HAVE_MPI_2 || defined(MPI_WIN_NULL)
#define HAVE_MPI_WIN_NULL 1
#else
#define HAVE_MPI_WIN_NULL 0
#endif
#endif

#ifndef HAVE_MPI_WIN_CREATE
#if HAVE_MPI_2
#define HAVE_MPI_WIN_CREATE 1
#else
#define HAVE_MPI_WIN_CREATE 0
#endif
#endif

#ifndef HAVE_MPI_WIN_FREE
#if HAVE_MPI_2
#define HAVE_MPI_WIN_FREE 1
#else
#define HAVE_MPI_WIN_FREE 0
#endif
#endif

#ifndef HAVE_MPI_WIN_TEST
#if HAVE_MPI_2
#define HAVE_MPI_WIN_TEST 1
#else
#define HAVE_MPI_WIN_TEST 0
#endif
#endif

#ifndef HAVE_MPI_WIN_LOCK
#if HAVE_MPI_2
#define HAVE_MPI_WIN_LOCK 1
#else
#define HAVE_MPI_WIN_LOCK 0
#endif
#endif

#ifndef HAVE_MPI_WIN_UNLOCK
#if HAVE_MPI_2
#define HAVE_MPI_WIN_UNLOCK 1
#else
#define HAVE_MPI_WIN_UNLOCK 0
#endif
#endif

#ifndef HAVE_MPI_MODE_NOCHECK
#if HAVE_MPI_2
#define HAVE_MPI_MODE_NOCHECK 1
#else
#define HAVE_MPI_MODE_NOCHECK 0
#endif
#endif

#ifndef HAVE_MPI_MODE_NOSTORE
#if HAVE_MPI_2
#define HAVE_MPI_MODE_NOSTORE 1
#else
#define HAVE_MPI_MODE_NOSTORE 0
#endif
#endif

#ifndef HAVE_MPI_MODE_NOPUT
#if HAVE_MPI_2
#define HAVE_MPI_MODE_NOPUT 1
#else
#define HAVE_MPI_MODE_NOPUT 0
#endif
#endif

#ifndef HAVE_MPI_MODE_NOPRECEDE
#if HAVE_MPI_2
#define HAVE_MPI_MODE_NOPRECEDE 1
#else
#define HAVE_MPI_MODE_NOPRECEDE 0
#endif
#endif

#ifndef HAVE_MPI_MODE_NOSUCCEED
#if HAVE_MPI_2
#define HAVE_MPI_MODE_NOSUCCEED 1
#else
#define HAVE_MPI_MODE_NOSUCCEED 0
#endif
#endif

#ifndef HAVE_MPI_LOCK_EXCLUSIVE
#if HAVE_MPI_2
#define HAVE_MPI_LOCK_EXCLUSIVE 1
#else
#define HAVE_MPI_LOCK_EXCLUSIVE 0
#endif
#endif

#ifndef HAVE_MPI_LOCK_SHARED
#if HAVE_MPI_2
#define HAVE_MPI_LOCK_SHARED 1
#else
#define HAVE_MPI_LOCK_SHARED 0
#endif
#endif

#ifndef HAVE_MPI_ERR_WIN
#if HAVE_MPI_2
#define HAVE_MPI_ERR_WIN 1
#else
#define HAVE_MPI_ERR_WIN 0
#endif
#endif

#ifndef HAVE_MPI_ERR_BASE
#if HAVE_MPI_2
#define HAVE_MPI_ERR_BASE 1
#else
#define HAVE_MPI_ERR_BASE 0
#endif
#endif

#ifndef HAVE_MPI_ERR_SIZE
#if HAVE_MPI_2
#define HAVE_MPI_ERR_SIZE 1
#else
#define HAVE_MPI_ERR_SIZE 0
#endif
#endif

#ifndef HAVE_MPI_ERR_DISP
#if HAVE_MPI_2
#define HAVE_MPI_ERR_DISP 1
#else
#define HAVE_MPI_ERR_DISP 0
#endif
#endif

#ifndef HAVE_MPI_ERR_LOCKTYPE
#if HAVE_MPI_2
#define HAVE_MPI_ERR_LOCKTYPE 1
#else
#define HAVE_MPI_ERR_LOCKTYPE 0
#endif
#endif

#ifndef HAVE_MPI_ERR_ASSERT
#if HAVE_MPI_2
#define HAVE_MPI_ERR_ASSERT 1
#else
#define HAVE_MPI_ERR_ASSERT 0
#endif
#endif

#ifndef HAVE_MPI_ERR_ASSERT
#if HAVE_MPI_2
#define HAVE_MPI_ERR_ASSERT 1
#else
#define HAVE_MPI_ERR_ASSERT 0
#endif
#endif

#ifndef HAVE_MPI_ERR_RMA_CONFLICT
#if HAVE_MPI_2
#define HAVE_MPI_ERR_RMA_CONFLICT 1
#else
#define HAVE_MPI_ERR_RMA_CONFLICT 0
#endif
#endif

#ifndef HAVE_MPI_ERR_RMA_SYNC
#if HAVE_MPI_2
#define HAVE_MPI_ERR_RMA_SYNC 1
#else
#define HAVE_MPI_ERR_RMA_SYNC 0
#endif
#endif


#ifndef HAVE_MPI_REPLACE
#if HAVE_MPI_2
#define HAVE_MPI_REPLACE 1
#else
#define HAVE_MPI_REPLACE 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_FILE_NULL
#if HAVE_MPI_2 || defined(MPI_FILE_NULL)
#define HAVE_MPI_FILE_NULL 1
#else
#define HAVE_MPI_FILE_NULL 0
#endif
#endif

#ifndef HAVE_MPI_FILE_OPEN
#if HAVE_MPI_2
#define HAVE_MPI_FILE_OPEN 1
#else
#define HAVE_MPI_FILE_OPEN 0
#endif
#endif

#ifndef HAVE_MPI_FILE_CLOSE
#if HAVE_MPI_2
#define HAVE_MPI_FILE_CLOSE 1
#else
#define HAVE_MPI_FILE_CLOSE 0
#endif
#endif

#ifndef HAVE_MPI_MODE_RDONLY
#if HAVE_MPI_2
#define HAVE_MPI_MODE_RDONLY 1
#else
#define HAVE_MPI_MODE_RDONLY 0
#endif
#endif

#ifndef HAVE_MPI_MODE_RDWR
#if HAVE_MPI_2
#define HAVE_MPI_MODE_RDWR 1
#else
#define HAVE_MPI_MODE_RDWR 0
#endif
#endif

#ifndef HAVE_MPI_MODE_WRONLY
#if HAVE_MPI_2
#define HAVE_MPI_MODE_WRONLY 1
#else
#define HAVE_MPI_MODE_WRONLY 0
#endif
#endif

#ifndef HAVE_MPI_MODE_CREATE
#if HAVE_MPI_2
#define HAVE_MPI_MODE_CREATE 1
#else
#define HAVE_MPI_MODE_CREATE 0
#endif
#endif

#ifndef HAVE_MPI_MODE_EXCL
#if HAVE_MPI_2
#define HAVE_MPI_MODE_EXCL 1
#else
#define HAVE_MPI_MODE_EXCL 0
#endif
#endif

#ifndef HAVE_MPI_MODE_DELETE_ON_CLOSE
#if HAVE_MPI_2
#define HAVE_MPI_MODE_DELETE_ON_CLOSE 1
#else
#define HAVE_MPI_MODE_DELETE_ON_CLOSE 0
#endif
#endif

#ifndef HAVE_MPI_MODE_UNIQUE_OPEN
#if HAVE_MPI_2
#define HAVE_MPI_MODE_UNIQUE_OPEN 1
#else
#define HAVE_MPI_MODE_UNIQUE_OPEN 0
#endif
#endif

#ifndef HAVE_MPI_MODE_SEQUENTIAL
#if HAVE_MPI_2
#define HAVE_MPI_MODE_SEQUENTIAL 1
#else
#define HAVE_MPI_MODE_SEQUENTIAL 0
#endif
#endif

#ifndef HAVE_MPI_MODE_APPEND
#if HAVE_MPI_2
#define HAVE_MPI_MODE_APPEND 1
#else
#define HAVE_MPI_MODE_APPEND 0
#endif
#endif

#ifndef HAVE_MPI_SEEK_SET
#if HAVE_MPI_2
#define HAVE_MPI_SEEK_SET 1
#else
#define HAVE_MPI_SEEK_SET 0
#endif
#endif

#ifndef HAVE_MPI_SEEK_CUR
#if HAVE_MPI_2
#define HAVE_MPI_SEEK_CUR 1
#else
#define HAVE_MPI_SEEK_CUR 0
#endif
#endif

#ifndef HAVE_MPI_SEEK_END
#if HAVE_MPI_2
#define HAVE_MPI_SEEK_END 1
#else
#define HAVE_MPI_SEEK_END 0
#endif
#endif

#ifndef HAVE_MPI_DISPLACEMENT_CURRENT
#if HAVE_MPI_2
#define HAVE_MPI_DISPLACEMENT_CURRENT 1
#else
#define HAVE_MPI_DISPLACEMENT_CURRENT 0
#endif
#endif

#ifndef HAVE_MPI_ERR_FILE
#if HAVE_MPI_2
#define HAVE_MPI_ERR_FILE 1
#else
#define HAVE_MPI_ERR_FILE 0
#endif
#endif

#ifndef HAVE_MPI_MAX_DATAREP_STRING
#if HAVE_MPI_2
#define HAVE_MPI_MAX_DATAREP_STRING 1
#else
#define HAVE_MPI_MAX_DATAREP_STRING 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_ALLOC_MEM
#if HAVE_MPI_2
#define HAVE_MPI_ALLOC_MEM 1
#else
#define HAVE_MPI_ALLOC_MEM 0
#endif
#endif

#ifndef HAVE_MPI_FREE_MEM
#if HAVE_MPI_2
#define HAVE_MPI_FREE_MEM 1
#else
#define HAVE_MPI_FREE_MEM 0
#endif
#endif

#ifndef HAVE_MPI_ERR_NO_MEM
#if HAVE_MPI_2
#define HAVE_MPI_ERR_NO_MEM 1
#else
#define HAVE_MPI_ERR_NO_MEM 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_OPEN_PORT
#if HAVE_MPI_2
#define HAVE_MPI_OPEN_PORT 1
#else
#define HAVE_MPI_OPEN_PORT 0
#endif
#endif

#ifndef HAVE_MPI_CLOSE_PORT
#if HAVE_MPI_2
#define HAVE_MPI_CLOSE_PORT 1
#else
#define HAVE_MPI_CLOSE_PORT 0
#endif
#endif

#ifndef HAVE_MPI_PUBLISH_NAME
#if HAVE_MPI_2
#define HAVE_MPI_PUBLISH_NAME 1
#else
#define HAVE_MPI_PUBLISH_NAME 0
#endif
#endif

#ifndef HAVE_MPI_UNPUBLISH_NAME
#if HAVE_MPI_2
#define HAVE_MPI_UNPUBLISH_NAME 1
#else
#define HAVE_MPI_UNPUBLISH_NAME 0
#endif
#endif

#ifndef HAVE_MPI_LOOKUP_NAME
#if HAVE_MPI_2
#define HAVE_MPI_LOOKUP_NAME 1
#else
#define HAVE_MPI_LOOKUP_NAME 0
#endif
#endif

#ifndef HAVE_MPI_COMM_ACCEPT
#if HAVE_MPI_2
#define HAVE_MPI_COMM_ACCEPT 1
#else
#define HAVE_MPI_COMM_ACCEPT 0
#endif
#endif

#ifndef HAVE_MPI_COMM_CONNECT
#if HAVE_MPI_2
#define HAVE_MPI_COMM_CONNECT 1
#else
#define HAVE_MPI_COMM_CONNECT 0
#endif
#endif

#ifndef HAVE_MPI_COMM_DISCONNECT
#if HAVE_MPI_2
#define HAVE_MPI_COMM_DISCONNECT 1
#else
#define HAVE_MPI_COMM_DISCONNECT 0
#endif
#endif

#ifndef HAVE_MPI_APPNUM
#if HAVE_MPI_2
#define HAVE_MPI_APPNUM 1
#else
#define HAVE_MPI_APPNUM 0
#endif
#endif

#ifndef HAVE_MPI_UNIVERSE_SIZE
#if HAVE_MPI_2
#define HAVE_MPI_UNIVERSE_SIZE 1
#else
#define HAVE_MPI_UNIVERSE_SIZE 0
#endif
#endif

#ifndef HAVE_MPI_ERRCODES_IGNORE
#if HAVE_MPI_2
#define HAVE_MPI_ERRCODES_IGNORE 1
#else
#define HAVE_MPI_ERRCODES_IGNORE 0
#endif
#endif

#ifndef HAVE_MPI_COMM_SPAWN
#if HAVE_MPI_2
#define HAVE_MPI_COMM_SPAWN 1
#else
#define HAVE_MPI_COMM_SPAWN 0
#endif
#endif

#ifndef HAVE_MPI_COMM_GET_PARENT
#if HAVE_MPI_2
#define HAVE_MPI_COMM_GET_PARENT 1
#else
#define HAVE_MPI_COMM_GET_PARENT 0
#endif
#endif

#ifndef HAVE_MPI_COMM_JOIN
#if HAVE_MPI_2
#define HAVE_MPI_COMM_JOIN 1
#else
#define HAVE_MPI_COMM_JOIN 0
#endif
#endif

#ifndef HAVE_MPI_ERR_NAME
#if HAVE_MPI_2
#define HAVE_MPI_ERR_NAME 1
#else
#define HAVE_MPI_ERR_NAME 0
#endif
#endif

#ifndef HAVE_MPI_ERR_PORT
#if HAVE_MPI_2
#define HAVE_MPI_ERR_PORT 1
#else
#define HAVE_MPI_ERR_PORT 0
#endif
#endif

#ifndef HAVE_MPI_ERR_SERVICE
#if HAVE_MPI_2
#define HAVE_MPI_ERR_SERVICE 1
#else
#define HAVE_MPI_ERR_SERVICE 0
#endif
#endif

#ifndef HAVE_MPI_ERR_SPAWN
#if HAVE_MPI_2
#define HAVE_MPI_ERR_SPAWN 1
#else
#define HAVE_MPI_ERR_SPAWN 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_MAX_OBJECT_NAME
#if HAVE_MPI_2
#define HAVE_MPI_MAX_OBJECT_NAME 1
#else
#define HAVE_MPI_MAX_OBJECT_NAME 0
#endif
#endif

#ifndef HAVE_MPI_COMM_GET_NAME
#if HAVE_MPI_2
#define HAVE_MPI_COMM_GET_NAME 1
#else
#define HAVE_MPI_COMM_GET_NAME 0
#endif
#endif

#ifndef HAVE_MPI_COMM_SET_NAME
#if HAVE_MPI_2
#define HAVE_MPI_COMM_SET_NAME 1
#else
#define HAVE_MPI_COMM_SET_NAME 0
#endif
#endif

#ifndef HAVE_MPI_TYPE_GET_NAME
#if HAVE_MPI_2
#define HAVE_MPI_TYPE_GET_NAME 1
#else
#define HAVE_MPI_TYPE_GET_NAME 0
#endif
#endif

#ifndef HAVE_MPI_WIN_SET_NAME
#if HAVE_MPI_2
#define HAVE_MPI_WIN_SET_NAME 1
#else
#define HAVE_MPI_WIN_SET_NAME 0
#endif
#endif

#ifndef HAVE_MPI_WIN_GET_NAME
#if HAVE_MPI_2
#define HAVE_MPI_WIN_GET_NAME 1
#else
#define HAVE_MPI_WIN_GET_NAME 0
#endif
#endif

#ifndef HAVE_MPI_WIN_SET_NAME
#if HAVE_MPI_2
#define HAVE_MPI_WIN_SET_NAME 1
#else
#define HAVE_MPI_WIN_SET_NAME 0
#endif
#endif

/* ---------------------------------------------------------------- */

#ifndef HAVE_MPI_ERR_KEYVAL
#if HAVE_MPI_2
#define HAVE_MPI_ERR_KEYVAL 1
#else
#define HAVE_MPI_ERR_KEYVAL 0
#endif
#endif

/* ---------------------------------------------------------------- */

#endif /* !Py_MPI4PY_CONFIG_H */
