# Author:    Lisandro Dalcin
# Contact:   dalcinl@gmail.com
# Copyright: This module has been placed in the public domain.
# Id:        $Id: MPI.py 165 2008-02-04 21:29:08Z dalcinl $

"""
Message Passing Interface module.

This module provides MPI support to run Python scripts in parallel
environments. It is constructed on top of the MPI-1/MPI-2
specification, but provides an object oriented interface which closely
follows the standard MPI-2 C++ bindings. Almost all MPI-2 features are
available provided that the underlying MPI implementation supports
them.

Any *picklable* Python object can be communicated, as well as objects
exposing single-segment buffer interface. There is support for
point-to-point (sends, receives), collective (broadcasts, scatters,
gathers, reductions), and one-sided (put, get, accumulate)
communications, as well as parallel file I/O (read, write)
operations. Group and communicator (inter, intra and topologies)
management is fully supported, as well as creation of user-defined
datatypes.
"""

__docformat__ = 'reStructuredText'


# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

__author__    = 'Lisandro Dalcin'
__credits__   = 'MPI Forum, MPICH Team, Open MPI Team.'
__version__   = '0.6.0'
__revision__  = '$Id: MPI.py 165 2008-02-04 21:29:08Z dalcinl $'


# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------

import mpi4py._mpi     as _mpi      # extension module
import mpi4py._op      as _op       # reduction operations
import mpi4py._pickle  as _pickle   # pickling support
import mpi4py._marshal as _marshal  # marshal support


# --------------------------------------------------------------------
# Serializers
# --------------------------------------------------------------------

class Pickle(object):

    """
    Serializer for any *picklable* Python object, implemented with
    ``cPickle`` and ``cStringIO`` modules.

    .. note:: This serializer is implemented using ``cPickle``
       functions ``dump()``/``dumps()`` and ``load()``/``loads()``,
       and it uses protocol ``HIGHEST_PROTOCOL`` by default.

    .. warning:: Using ``cPickle`` protocol ``HIGHEST_PROTOCOL`` could
       be problematic when a parallel applications runs in an
       heterogeneous environment. In such a case, you can change the
       attribute `PROTOCOL` of this class, or even change the
       attribute ``SERIALIZER`` of ``Comm`` class.
    """

    PROTOCOL = _pickle.HIGH_PROT
    dump = classmethod(_pickle.dump)
    load = classmethod(_pickle.load)

    def __new__(cls, *targs, **kargs):
        from types import MethodType as method
        pkl = object.__new__(cls)
        if cls is Pickle or 'dump' not in cls.__dict__:
            pkl.dump = method(_pickle.dump, pkl, cls)
        if cls is Pickle or 'load' not in cls.__dict__:
            pkl.load = method(_pickle.load, pkl, cls)
        return pkl

    def __init__(self, protocol=_pickle.HIGH_PROT):
        self.PROTOCOL = protocol


class Marshal(object):

    """
    Serializer for any *marshable* Python object, implemented
    with ``marshal`` module.

    .. note:: The binary format is specific to Python, but independent
       of machine architecture.

    .. warning:: This serializer inherits the limitations of
       ``marshal`` module.
    """

    PROTOCOL = _marshal.VERSION
    dump = classmethod(_marshal.dump)
    load = classmethod(_marshal.load)

    def __new__(cls, *targs, **kargs):
        from types import MethodType as method
        msh = object.__new__(cls)
        if cls is Marshal or 'dump' not in cls.__dict__:
            msh.dump = method(_marshal.dump, msh, cls)
        if cls is Marshal or 'load' not in cls.__dict__:
            msh.load = method(_marshal.load, msh, cls)
        return msh

    def __init__(self, protocol=_marshal.VERSION):
        self.PROTOCOL = protocol


# --------------------------------------------------------------------
# Buffer
# --------------------------------------------------------------------

def Buffer(*args):
    """
    Buffer(data[[, count], datatype]) -> tuple

    Return a 3-tuple ``(data, count, datatype)`` representing a memory
    buffer involved in a communication operation.

    :Parameters:
        - `data`: Any Python object exporting single-segment
          buffer interface. Alternatively, it can also be a
          2-tuple with ``(pointer, read-only flag)``, where
          ``pointer`` can be either a integer (a long integer if
          necessary) or hexadecimal string representing a valid
          memory address pointing to the start of a contiguous
          memory buffer, and ``read-only flag`` is a boolean
          indicating whether the memory referenced by ``pointer``
          is read-only or not (``True`` means read-only, ``False``
          means writable).
        - `count`: Number of entries in `data` acording to `datatype`
          (optional, defaults to ``None``). If it is omitted or
          ``None``, the number or entries will be guessed from the
          size of the buffer referenced by `data`, but in such a case
          `datatype` is currently required to have the same size and
          extent.
        - `datatype`: Any valid MPI datatype of each entry in the
          memory buffer represented by `data` (optional, defaults to
          ``BYTE``).

    :Exceptions:
        - `AssertionError` if `count` is not integer or ``None``,
          or `datatype` is not an instance of `Datatype`.
    """
    data = None
    count = None
    datatype = BYTE
    if args:
        if len(args) == 1:
            (data, ) = args
        if len(args) == 2:
            (data, datatype, ) = args
        elif len(args) == 3:
            (data, count, datatype) = args
        else:
            raise TypeError('Buffer() takes at most 3 arguments '
                            '(%d given))' % (len(args) + 1))
    try:
        _ints = (int, long)
    except NameError:
        _ints = (int, )
    assert isinstance(count, _ints) or count is None
    assert isinstance(datatype, Datatype)
    return (data, count, datatype)


# --------------------------------------------------------------------
# Assorted constants
# --------------------------------------------------------------------

UNDEFINED = _mpi.UNDEFINED
"""Undefined integer value"""
PROC_NULL = _mpi.PROC_NULL
"""Special process rank for send/receive"""
ANY_SOURCE = _mpi.ANY_SOURCE
"""Wildcard source value for receives"""
ROOT = _mpi.ROOT
"""Root process for collective inter-communications"""
ANY_TAG = _mpi.ANY_TAG
"""Wildcard tag value for receives"""
BSEND_OVERHEAD = _mpi.BSEND_OVERHEAD
"""Upper bound of memory overhead for sending in buffered mode"""
BOTTOM = _mpi.BOTTOM
"""Special address for buffers"""
IN_PLACE = _mpi.IN_PLACE
"""*In-place* option for collective communications"""



# --------------------------------------------------------------------
# Datatype
# --------------------------------------------------------------------

# Storage order for arrays.

ORDER_C = _mpi.ORDER_C
"""C order (row major)"""
ORDER_FORTRAN = _mpi.ORDER_FORTRAN
"""Fortran order (column major)"""

# Type of distributions for HPF-like distributed arrays

DISTRIBUTE_NONE = _mpi.DISTRIBUTE_NONE
"""Dimension not distributed"""
DISTRIBUTE_BLOCK = _mpi.DISTRIBUTE_BLOCK
"""Mlock distribution"""
DISTRIBUTE_CYCLIC = _mpi.DISTRIBUTE_CYCLIC
"""Cyclic distribution"""
DISTRIBUTE_DFLT_DARG = _mpi.DISTRIBUTE_DFLT_DARG
"""Default distribution argument"""

class Datatype(_mpi.Datatype):

    """
    Datatype class.
    """

    def __init__(self, datatype=None):
        _mpi.Datatype.__init__(self, datatype)

    # Datatype Accessors
    # ------------------

    def Get_extent(self):
        """
        Return lower bound and extent of datatype.
        """
        return _mpi.type_get_extent(self)

    def Get_size(self):
        """
        Return the number of bytes occupied by entries in the
        datatype.
        """
        return _mpi.type_size(self)

    # Datatype Constructors
    # ---------------------

    def Dup(self):
        """
        Duplicate a datatype.
        """
        newtype = _mpi.type_dup(self)
        return type(self)(newtype)

    def Create_contiguous(self, count):
        """
        Create a contiguous datatype.
        """
        newtype = _mpi.type_contiguous(count, self)
        return type(self)(newtype)

    def Create_vector(self, count, blocklength, stride):
        """
        Create a vector (strided) datatype.
        """
        newtype = _mpi.type_vector(count, blocklength, stride, self)
        return type(self)(newtype)

    def Create_hvector(self, count, blocklength, stride):
        """
        Create a vector (strided) datatype.
        """
        newtype = _mpi.type_hvector(count, blocklength, stride, self)
        return type(self)(newtype)

    def Create_indexed(self, blocklengths, displacements):
        """
        Create a indexed datatype.
        """
        newtype = _mpi.type_indexed(blocklengths, displacements, self)
        return type(self)(newtype)

    def Create_indexed_block(self, blocklength, displacements):
        """
        Create a indexed datatype with constant-sized blocks.
        """
        newtype = _mpi.type_indexed_block(blocklength,
                                          displacements, self)
        return type(self)(newtype)

    def Create_hindexed(self, blocklengths, displacements):
        """
        Create a indexed datatype with displacements in bytes.
        """
        newtype = _mpi.type_hindexed(blocklengths, displacements, self)
        return type(self)(newtype)

    def Create_subarray(self, sizes, subsizes, starts, order=None):
        """
        Create a datatype for a subarray of a regular,
        multidimensional array.
        """
        newtype = _mpi.type_subarray(sizes, subsizes, starts,
                                     order, self)
        return type(self)(newtype)

    def Create_darray(self, size, rank,
                      gsizes, distribs, dargs, psizes,
                      order=None):
        """
        Create a datatype representing an array distributed HPF-like
        on Cartesian process grids.
        """
        newtype = _mpi.type_darray(size, rank, gsizes, distribs,
                                   dargs, psizes, order, self)
        return type(self)(newtype)

    ## @classmethod
    def Create_struct(cls, blocklengths, displacements, datatypes):
        """
        Create an datatype from a general set of
        block sizes, displacements and datatypes.
        """
        newtype = _mpi.type_struct(blocklengths,
                                   displacements,
                                   datatypes)
        return cls(newtype)

    Create_struct = classmethod(Create_struct)

    # Size-specific Datatypes
    # -----------------------

    ## @classmethod
    def Match_size(cls, typeclass, size):
        """
        Find a datatype matching a specified size in bytes.
        """
        newtype = _mpi.type_match_size(typeclass, size)
        return cls(newtype)

    Match_size = classmethod(Match_size)

    # Use of Derived Datatypes
    # ------------------------

    def Commit(self):
        """
        Commit the datatype.
        """
        _mpi.type_commit(self)

    def Free(self):
        """
        Free the datatype.
        """
        _mpi.type_free(self)

    # Datatype Resizing
    # -----------------

    def Create_resized(self, lb, extent):
        """
        Create a datatype with a new lower bound and extent.
        """
        newtype = _mpi.type_resized(self, lb, extent)
        return type(self)(newtype)

    Resized = Create_resized

    def Get_true_extent(self):
        """
        Return the true lower bound and extent of datatype.
        """
        return _mpi.type_true_extent(self)

    # Pack and Unpack
    # ---------------

    def Pack(self, inbuf, outbuf, position, comm):
        """
        Pack into contiguous memory according to datatype.
        """
        return _mpi.pack(inbuf, self, outbuf, position, comm)

    def Unpack(self, inbuf, position, outbuf, comm):
        """
        Unpack from contiguous memory according to datatype.
        """
        return _mpi.unpack(inbuf, position, outbuf, self, comm)

    def Pack_size(self, count, comm):
        """
        Returns the upper bound on the amount of space (in bytes)
        needed to pack a message according to datatype.
        """
        return _mpi.pack_size(count, self, comm)

    # Canonical Pack and Unpack
    # -------------------------

    def Pack_external(self, datarep, inbuf, outbuf, position):
        """
        Pack into contiguous memory according to datatype,
        using the **external32** format.
        """
        return _mpi.pack_external(datarep, inbuf,
                                  self, outbuf, position)

    def Unpack_external(self, datarep, inbuf, position, outbuf):
        """
        Unpack from contiguous memory according to datatype,
        using the **external32** format.
        """
        return _mpi.unpack_external(datarep, inbuf, position,
                                    outbuf, self)

    def Pack_external_size(self, datarep, count):
        """
        Returns the upper bound on the amount of space (in bytes)
        needed to pack a message according to datatype,
        using the **external32** format.
        """
        return _mpi.pack_external_size(datarep, count, self)

    # Naming Objects
    # --------------

    def Get_name(self):
        """
        Get the print name from this datatype.
        """
        return _mpi.type_get_name(self)

    def Set_name(self, name):
        """
        Set the print name for this datatype.
        """
        return _mpi.type_set_name(self, name)

    # Properties
    # ----------

    size   = property(_mpi.type_size, doc="datatype size, in bytes")
    extent = property(_mpi.type_ex,   doc="datatype extent")
    lb     = property(_mpi.type_lb,   doc="datatype lower bound")
    ub     = property(_mpi.type_ub,   doc="datatype upper bound")

    name = property(_mpi.type_get_name,
                    _mpi.type_set_name,
                    doc="datatype name")


# Predefined datatype handles
# ---------------------------

DATATYPE_NULL  = Datatype(_mpi.DATATYPE_NULL)
"""Null datatype handle"""
# Elementary datatypes
CHAR            = Datatype(_mpi.CHAR)
WCHAR           = Datatype(_mpi.WCHAR)
SIGNED_CHAR     = Datatype(_mpi.SIGNED_CHAR)
UNSIGNED_CHAR   = Datatype(_mpi.UNSIGNED_CHAR)
SHORT           = Datatype(_mpi.SHORT)
UNSIGNED_SHORT  = Datatype(_mpi.UNSIGNED_SHORT)
INT             = Datatype(_mpi.INT)
UNSIGNED        = Datatype(_mpi.UNSIGNED)
UNSIGNED_INT    = UNSIGNED
LONG            = Datatype(_mpi.LONG)
UNSIGNED_LONG   = Datatype(_mpi.UNSIGNED_LONG)
FLOAT           = Datatype(_mpi.FLOAT)
DOUBLE          = Datatype(_mpi.DOUBLE)
LONG_DOUBLE     = Datatype(_mpi.LONG_DOUBLE)
BYTE            = Datatype(_mpi.BYTE)
PACKED          = Datatype(_mpi.PACKED)
# Datatypes for reduction operations
SHORT_INT       = Datatype(_mpi.SHORT_INT)
TWOINT          = Datatype(_mpi.TWOINT)
INT_INT         = TWOINT
LONG_INT        = Datatype(_mpi.LONG_INT)
FLOAT_INT       = Datatype(_mpi.FLOAT_INT)
DOUBLE_INT      = Datatype(_mpi.DOUBLE_INT)
LONG_DOUBLE_INT = Datatype(_mpi.LONG_DOUBLE_INT)
# Optional datatypes
LONG_LONG          = Datatype(_mpi.LONG_LONG)
UNSIGNED_LONG_LONG = Datatype(_mpi.UNSIGNED_LONG_LONG)
LONG_LONG_INT      = Datatype(_mpi.LONG_LONG_INT)
# Special datatypes (for constructing derived datatypes)
UB = Datatype(_mpi.UB) #: upper-bound marker (deprecated in MPI-2)
LB = Datatype(_mpi.LB) #: lower-bound marker (deprecated in MPI-2)



# --------------------------------------------------------------------
# Memory
# --------------------------------------------------------------------

# Address Function
# ----------------

def Get_address(location):
    """
    Get the address of a location in memory.
    """
    return _mpi.get_address(location)


# Memory Allocation
# -----------------

def Alloc_mem(size, info=None):
    """
    Allocate memory for message passing and RMA.
    """
    return _mpi.alloc_mem(size, info)

def Free_mem(base):
    """
    Free memory allocated with `Alloc_mem()`.
    """
    return _mpi.free_mem(base)


# Buffer Allocation and Usage
# ---------------------------

def Attach_buffer(buf):
    """
    Attach a user-provided buffer for sending in buffered mode.
    """
    return _mpi.buffer_attach(buf)

def Detach_buffer():
    """
    Remove an existing attached buffer.
    """
    return _mpi.buffer_detach()



# --------------------------------------------------------------------
# Status
# --------------------------------------------------------------------

class Status(_mpi.Status):

    """
    Status class.
    """

    def __init__(self, status=None):
        _mpi.Status.__init__(self, status)

    def Get_source(self):
        """
        Get message source.
        """
        return self.MPI_SOURCE

    def Get_tag(self):
        """
        Get message tag.
        """
        return self.MPI_TAG

    def Get_error(self):
        """
        Get message error.
        """
        return self.MPI_ERROR

    def Set_source(self, source):
        """
        Set message surce.
        """
        self.MPI_SOURCE = source

    def Set_tag(self, tag):
        """
        Set message tag.
        """
        self.MPI_TAG = tag

    def Set_error(self, error):
        """
        Set message error.
        """
        self.MPI_ERROR = error

    def Get_count(self, datatype=None):
        """
        Get the number of *top level* elements.

        .. note:: Currently, `datatype` defaults to `BYTE`.
        """
        if datatype is None:
            datatype = BYTE
        return _mpi.get_count(self, datatype)

    def Get_elements(self, datatype=None):
        """
        Get the number of basic elements in a datatype.

        .. note:: Currently, `datatype` defaults to `BYTE`.
        """
        if datatype is None:
            datatype = BYTE
        return _mpi.get_elements(self, datatype)

    def Is_cancelled(self):
        """
        Test to see if a request was cancelled.
        """
        return _mpi.test_cancelled(self)

    def Set_elements(self, datatype, count):
        """
        Set the number of elements in a status.

        .. note:: Currently, if `datatype` is ``None``, datatype
          `BYTE` is used instead.

        .. note:: This should be only used for implementing
           query callback functions generalized requests.
        """
        if datatype is None:
            datatype = BYTE
        return _mpi.status_set_elements(self, datatype, count)

    def Set_cancelled(self, flag):
        """
        Set the cancelled state associated with a status.

        .. note:: This should be only used for implementing
           query callback functions generalized requests.
        """
        return _mpi.status_set_cancelled(self, bool(flag))


    # Properties
    # ----------

    source = property(Get_source, Set_source, doc='message source')
    tag    = property(Get_tag,    Set_tag,    doc='message tag')
    error  = property(Get_error,  Set_error,  doc='message error')



# --------------------------------------------------------------------
# Request
# --------------------------------------------------------------------

class Request(_mpi.Request):

    """
    Request class.
    """

    def __init__(self, request=None):
        _mpi.Request.__init__(self, request)

    # Completion Operations
    # ---------------------

    def Wait(self, status=None):
        """
        Wait for an MPI send or receive to complete.
        """
        return _mpi.wait(self, status)

    def Test(self, status=None):
        """
        Test for the completion of a send or receive.
        """
        return _mpi.test(self, status)

    def Free(self):
        """
        Free a communication request object.
        """
        return _mpi.request_free(self)

    def Get_status(self, status=None):
        """
        Nondestructive test for the completion of a request.
        """
        return _mpi.request_get_status(self, status)

    # Multiple Completions
    # --------------------

    ## @staticmethod
    def Waitany(requests, status=None):
        """
        Wait for any previously initiated request to complete.
        """
        return _mpi.waitany(requests, status)

    Waitany = staticmethod(Waitany)

    ## @staticmethod
    def Testany(requests, status=None):
        """
        Test for completion of any previously initiated request.
        """
        return _mpi.testany(requests, status)

    Testany = staticmethod(Testany)

    ## @staticmethod
    def Waitall(requests, statuses=None):
        """
        Wait for all previously initiated requests to complete.
        """
        return _mpi.waitall(requests, statuses)

    Waitall = staticmethod(Waitall)

    ## @staticmethod
    def Testall(requests, statuses=None):
        """
        Test for completion of all previously initiated requests.
        """
        return _mpi.testall(requests, statuses)

    Testall = staticmethod(Testall)

    ## @staticmethod
    def Waitsome(requests, statuses=None):
        """
        Wait for some previously initiated requests to complete.
        """
        return _mpi.waitsome(requests, statuses)

    Waitsome = staticmethod(Waitsome)

    ## @staticmethod
    def Testsome(requests, statuses=None):
        """
        Test for completion of some previously initiated requests.
        """
        return _mpi.testsome(requests, statuses)

    Testsome = staticmethod(Testsome)

    # Cancel
    # ------

    def Cancel(self):
        """
        Cancel a communication request.
        """
        return _mpi.cancel(self)


class Prequest(Request):

    """
    Persistent Request class.
    """

    def __init__(self, prequest=None):
        Request.__init__(self, prequest)

    def Start(self):
        """
        Initiate a communication with a persistent request.
        """
        _mpi.start(self)

    ## @staticmethod
    def Startall(requests):
        """
        Start a collection of persistent requests.
        """
        _mpi.startall(requests)

    Startall = staticmethod(Startall)


class Grequest(Request):

    """
    Generalized Request class.
    """

    def __init__(self, grequest=None):
        Request.__init__(self, grequest)

    ## @classmethod
    def Start(cls, query_fn, free_fn, cancel_fn, extra_state):
        """
        Create and return a user-defined request.
        """
        newgreq = _mpi.grequest_start(query_fn,
                                      free_fn,
                                      cancel_fn,
                                      extra_state)
        return cls(newgreq)

    Start = classmethod(Start)

    def Complete(self):
        """
        Notify MPI that a user-defined request is complete.
        """
        _mpi.grequest_complete(self)


# Predefined request handle
# -------------------------

REQUEST_NULL = Request(_mpi.REQUEST_NULL)
"""Null request handle"""



# --------------------------------------------------------------------
# Operations
# --------------------------------------------------------------------

class Op(_mpi.Op):

    """
    Op class.
    """

    def __new__(cls, op=None, *targs, **kargs):
        newop = _mpi.Op.__new__(cls, op)
        if newop is not op:
            if targs or kargs:
                newop.Init(*targs, **kargs)
            else:
                newop.Init(None, False)
        return newop

    def __init__(self, op=None, *targs, **kargs):
        _mpi.Op.__init__(self, op, *targs, **kargs)

    def __call__(self, x, y):
        """
        Call the user-defined combination function handle.
        """
        return self.__function(x, y)

    def Init(self, function, commute=False):
        """
        Create a user-defined combination function handle.
        """
        if hasattr(function, '__call__'):
            self.__function = function
            self.__commute  = bool(commute)
        else:
            if function is not None:
                _mpi.op_create(function, commute, self)
            self.__function = lambda x, y: _mpi._raise(_mpi.ERR_OP)
            self.__commute  = bool(commute)

    def Free(self):
        """
        Free a user-defined combination function handle.
        """
        _mpi.op_free(self)


# Predefined operations
#----------------------

OP_NULL = Op(_mpi.OP_NULL)
"""Null operation handle"""
MAX     = Op(_mpi.MAX,     _op.MAX,     True)  #: Maximum
MIN     = Op(_mpi.MIN,     _op.MIN,     True)  #: Minimum
SUM     = Op(_mpi.SUM,     _op.SUM,     True)  #: Sum
PROD    = Op(_mpi.PROD,    _op.PROD,    True)  #: Product
LAND    = Op(_mpi.LAND,    _op.LAND,    True)  #: Logical and
BAND    = Op(_mpi.BAND,    _op.BAND,    True)  #: Bit-wise and
LOR     = Op(_mpi.LOR,     _op.LOR,     True)  #: Logical or
BOR     = Op(_mpi.BOR,     _op.BOR,     True)  #: Bit-wise or
LXOR    = Op(_mpi.LXOR,    _op.LXOR,    True)  #: Logical xor
BXOR    = Op(_mpi.BXOR,    _op.BXOR,    True)  #: Bit-wise xor
MAXLOC  = Op(_mpi.MAXLOC,  _op.MAXLOC,  True)  #: Maximum and location
MINLOC  = Op(_mpi.MINLOC,  _op.MINLOC,  True)  #: Minimum and location
REPLACE = Op(_mpi.REPLACE, _op.REPLACE, False) #: Replace (for RMA)



# --------------------------------------------------------------------
# [4.10] The Info Object
# --------------------------------------------------------------------

class Info(_mpi.Info):

    """
    Info class
    """

    def __init__(self, info=None):
        _mpi.Info.__init__(self, info)

    ## @classmethod
    def Create(cls):
        """
        Create a new, empty info object.
        """
        info = _mpi.info_create()
        return cls(info)

    Create = classmethod(Create)

    def Dup(self):
        """
        Duplicate an existing info object, creating a new object, with
        the same (key, value) pairs and the same ordering of keys.
        """
        info = _mpi.info_dup(self)
        return type(self)(info)

    def Free(self):
        """
        Free a info object.

        .. note:: `self` will have a handle to ``MPI_INFO_NULL`` upon
           successful return.
        """
        _mpi.info_free(self)

    def Set(self, key, value):
        """
        Add the (key,value) pair to info, and overrides the value if a
        value for the same key was previously set.

        .. note:: If either `key` or `value` are larger than the
           allowed maximums, the errors `ERR_INFO_KEY` or
           `ERR_INFO_VALUE` are raised, respectively.
        """
        _mpi.info_set(self, key, value)

    def Delete(self, key):
        """
        Remove a (key,value) pair from info.

        .. note:: If `key` is not present, a error of class
          `ERR_INFO_NOKEY` is raised.
        """
        _mpi.info_delete(self, key)

    Del = Delete ##: convenience alias for `Info.Delete()`

    def Get(self, key, maxlen=-1):
        """
        Retrieve the value associated with a key.

        .. note:: If `key` is not present, ``None`` is returned.
        """
        return _mpi.info_get(self, key, maxlen)

    def Get_nkeys(self):
        """
        Return the number of currently defined keys in info.
        """
        return _mpi.info_get_nkeys(self)

    def Get_nthkey(self, n):
        """
        Return the nth defined key in info. Keys are numbered in the
        range [0, N) where N is the value returned by
        `Info.Get_nkeys()`.

        .. note:: All keys between 0 and N-1 are guaranteed to be
           defined. The number of a given key does not change as long
           as info is not modified with `Info.Set()` or
           `Info.Delete()`.
        """
        return _mpi.info_get_nthkey(self, n)

    # Mapping Methods
    # ---------------

    def __len__(self):
        if not self: return 0
        return _mpi.info_get_nkeys(self)

    def __getitem__(self, key):
        if not self: raise KeyError('info is INFO_NULL')
        value, flag = _mpi.info_get(self, key)
        if not flag: raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        if not self: raise KeyError('info is INFO_NULL')
        return _mpi.info_set(self, key, value)

    def __delitem__(self, key):
        if not self: raise KeyError('info is INFO_NULL')
        return _mpi.info_delete(self, key)

    def __contains__(self, key):
        if not self: return False
        return _mpi.info_get_valuelen(self, key)[1]

    def __iter__(self):
        if not self: return
        nkeys = _mpi.info_get_nkeys(self)
        nthkey = _mpi.info_get_nthkey
        try:    iterkeys = xrange
        except: iterkeys = range
        for k in iterkeys(nkeys):
            yield nthkey(self, k)


# Predefined info handle
# ------------------------

INFO_NULL = Info(_mpi.INFO_NULL)
"""Null info handle"""


# --------------------------------------------------------------------
# Group
# --------------------------------------------------------------------

class Group(_mpi.Group):

    """
    Group class.
    """

    def __init__(self, group=None):
        _mpi.Group.__init__(self, group)

    # Group Accessors
    # ---------------

    def Get_size(self):
        """
        Return the size of a group.
        """
        return _mpi.group_size(self)

    def Get_rank(self):
        """
        Return the rank of this process in the group.
        """
        return _mpi.group_rank(self)

    ## @staticmethod
    def Translate_ranks(group1, ranks1, group2):
        """
        Translate the ranks of processes in one group to those in
        another group.
        """
        return _mpi.group_transl_rank(group1, ranks1, group2)

    Translate_ranks = staticmethod(Translate_ranks)

    ## @staticmethod
    def Compare(group1, group2):
        """
        Compare two groups.
        """
        return _mpi.group_compare(group1, group2)

    Compare = staticmethod(Compare)

    # Group Constructors
    # ------------------

    ## @classmethod
    def Union(cls, group1, group2):
        """
        Produce a group by combining two groups.
        """
        newgroup = _mpi.group_union(group1, group2)
        return cls(newgroup)

    Union = classmethod(Union)

    ## @classmethod
    def Intersect(cls, group1, group2):
        """
        Produce a group as the intersection of two existing groups.
        """
        newgroup = _mpi.group_intersection(group1, group2)
        return cls(newgroup)

    Intersect = classmethod(Intersect)

    ## @classmethod
    def Difference(cls, group1, group2):
        """
        Make a group from the difference of two groups.
        """
        newgroup = _mpi.group_difference(group1, group2)
        return cls(newgroup)

    Difference = classmethod(Difference)

    def Incl(self, ranks):
        """
        Produce a group by reordering an existing group and taking
        only listed members.
        """
        newgroup = _mpi.group_incl(self, ranks)
        return type(self)(newgroup)

    def Excl(self, ranks):
        """
        Produce a group by reordering an existing group and taking
        only unlisted members.
        """
        newgroup = _mpi.group_excl(self, ranks)
        return type(self)(newgroup)

    def Range_incl(self, ranks):
        """
        Create a new group from ranges of ranks in an existing group.
        """
        newgroup = _mpi.group_range_incl(self, ranks)
        return type(self)(newgroup)

    def Range_excl(self, ranks):
        """
        Produce a group by excluding ranges of processes from an
        existing group.
        """
        newgroup = _mpi.group_range_excl(self, ranks)
        return type(self)(newgroup)

    # Group Destructor
    # ----------------

    def Free(self):
        """
        Free a group.

        .. note:: `self` will have a handle to ``MPI_GROUP_NULL`` upon
           successful return.
        """
        return _mpi.group_free(self)

    # Properties
    # ----------

    size = property(_mpi.group_size,
                    doc='number of processes in group')
    rank = property(_mpi.group_rank,
                    doc='rank of this process in group')


# Predefined group handles
# ------------------------

GROUP_NULL = Group(_mpi.GROUP_NULL)
"""Null group handle"""
GROUP_EMPTY = Group(_mpi.GROUP_EMPTY)
"""Empty group handle"""



# --------------------------------------------------------------------
# Communicator
# --------------------------------------------------------------------

# Comparisons

IDENT = _mpi.IDENT
"""Groups are identical, communicator contexts are de same"""
CONGRUENT = _mpi.CONGRUENT
"""Groups are identical, contexts are different """
SIMILAR = _mpi.SIMILAR
"""Groups are similar , rank order differs"""
UNEQUAL = _mpi.UNEQUAL
"""Groups are different"""

# Topologies

CART = _mpi.CART
"""Cartesian topology"""
GRAPH = _mpi.GRAPH
"""Graph topology"""

class Comm(_mpi.Comm):

    """
    Communicator class.
    """

    def __init__(self, comm=None):
        _mpi.Comm.__init__(self, comm)
        _mpi.comm_check_any(self)

    SERIALIZER = Pickle
    """Object Serializer"""

    # Group
    # -----

    def Get_group(self):
        """
        Access the group associated with a communicator.
        """
        group = _mpi.comm_group(self)
        return Group(group)

    # Communicator Accessors
    # ----------------------

    def Get_size(self):
        """
        Determine the size of the group associated with a
        communicator.
        """
        return _mpi.comm_size(self)

    def Get_rank(self):
        """
        Determine the rank of the calling process in the
        communicator.
        """
        return _mpi.comm_rank(self)

    ## @staticmethod
    def Compare(comm1, comm2):
        """
        Compare two communicators.
        """
        return _mpi.comm_compare(comm1, comm2)

    Compare = staticmethod(Compare)

    # Communicator Constructors
    # -------------------------

    def Clone(self):
        """
        Duplicate an existing communicator.
        """
        newcomm = _mpi.comm_dup(self)
        return type(self)(newcomm)

    # Communicator Destructors
    # ------------------------

    def Free(self):
        """
        Mark the communicator object for deallocation.

        .. note:: `self` will have a handle to ``MPI_COMM_NULL`` upon
           successful return.
        """
        _mpi.comm_free(self)

    # Point to Point communication
    # ----------------------------

    # Blocking Send and Receive Operations
    # ------------------------------------

    def Send(self, buf, dest=0, tag=0):
        """
        Blocking send.

        .. note:: This function may block until the message is
           received. Whether or not `Send` blocks depends on
           several factors and is implementation dependent.
        """
        buf, fastmode = _mpi.make_buf(buf)
        if fastmode:
            _mpi.send(buf, dest, tag, self)
            return None
        else:
            serializer = self.SERIALIZER
            send = _mpi.send_pickled
            if dest != _mpi.PROC_NULL:
                buf = serializer.dump(buf)
            else:
                buf = None
            send(buf, dest, tag, self)
            return None

    def Recv(self, buf=None, source=0, tag=0, status=None):
        """
        Blocking receive.

        .. note:: This function blocks until the message is received.
        """
        buf, fastmode = _mpi.make_buf(buf)
        if fastmode:
            _mpi.recv(buf, source, tag, self, status)
            return None
        else:
            serializer = self.SERIALIZER
            recv = _mpi.recv_pickled
            buf = recv(buf, source, tag, self, status)
            if source != _mpi.PROC_NULL:
                buf = serializer.load(buf)
            return buf

    # Send-Receive
    # ------------

    def Sendrecv(self, sendbuf, dest=0, sendtag=0,
                 recvbuf=None, source=0, recvtag=0,
                 status=None):
        """
        Send and receive a message.

        .. note:: This function is guaranteed not to deadlock in
           situations where pairs of blocking sends and receives may
           deadlock.

        .. caution:: A common mistake when using this function is to
           mismatch the tags with the source and destination ranks,
           which can result in deadlock.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.sendrecv(sendbuf, dest, sendtag,
                          recvbuf, source, recvtag,
                          self, status)
            return None
        else:
            serializer = self.SERIALIZER
            sendrecv = _mpi.sendrecv_pickled
            if dest != _mpi.PROC_NULL:
                sendbuf = serializer.dump(sendbuf)
            else:
                sendbuf = None
            recvbuf = sendrecv(sendbuf, dest, sendtag,
                               recvbuf, source, recvtag,
                               self, status)
            if recvbuf is not None:
                recvbuf = serializer.load(recvbuf)
            return recvbuf

    def Sendrecv_replace(self, buf,
                         dest=0, sendtag=0,
                         source=0, recvtag=0,
                         status=None):
        """
        Send and receive a message.

        .. note:: This function is guaranteed not to deadlock in
           situations where pairs of blocking sends and receives may
           deadlock.

        .. caution:: A common mistake when using this function is to
           mismatch the tags with the source and destination ranks,
           which can result in deadlock.
        """
        _mpi.sendrecv_replace(buf,
                              dest, sendtag,
                              source, recvtag,
                              self, status)
        return None

    # Nonblocking Communications
    # --------------------------

    def Isend(self, buf, dest=0, tag=0):
        """
        Nonblocking send.
        """
        request = _mpi.isend(buf, dest, tag, self)
        return Request(request)

    def Irecv(self, buf, source=0, tag=0):
        """
        Nonblocking receive.
        """
        request = _mpi.irecv(buf, source, tag, self)
        return Request(request)

    # Probe
    # -----

    def Probe(self, source=0, tag=0, status=None):
        """
        Blocking test for a message.

        .. note:: This function blocks until the message arrives.
        """
        return _mpi.probe(source, tag, self, status)

    def Iprobe(self, source=0, tag=0, status=None):
        """
        Nonblocking test for a message.
        """
        return _mpi.iprobe(source, tag, self, status)

    # Persistent Communication
    # ------------------------

    def Send_init(self, buf, dest=0, tag=0):
        """
        Create a persistent request for a standard send.
        """
        prequest = _mpi.send_init(buf, dest, tag, self)
        return Prequest(prequest)

    def Recv_init(self, buf, source=0, tag=0):
        """
        Create a persistent request for a receive.
        """
        prequest = _mpi.recv_init(buf, source, tag, self)
        return Prequest(prequest)

    # Communication Modes
    # -------------------

    # Blocking calls

    def Bsend(self, buf, dest=0, tag=0):
        """
        Blocking send in buffered mode.
        """
        return _mpi.send(buf, dest, tag, self, 'B')

    def Ssend(self, buf, dest=0, tag=0):
        """
        Blocking send in synchronous mode.
        """
        return _mpi.send(buf, dest, tag, self, 'S')

    def Rsend(self, buf, dest=0, tag=0):
        """
        Blocking send in ready mode.
        """
        return _mpi.send(buf, dest, tag, self, 'R')

    # Nonblocking calls

    def Ibsend(self, buf, dest=0, tag=0):
        """
        Nonblocking send in buffered mode.
        """
        request = _mpi.isend(buf, dest, tag, self, 'B')
        return Request(request)

    def Issend(self, buf, dest=0, tag=0):
        """
        Nonblocking send in synchronous mode.
        """
        request = _mpi.isend(buf, dest, tag, self, 'S')
        return Request(request)

    def Irsend(self, buf, dest=0, tag=0):
        """
        Nonblocking send in ready mode.
        """
        request = _mpi.isend(buf, dest, tag, self, 'R')
        return Request(request)

    # Persistent Requests

    def Bsend_init(self, buf, dest=0, tag=0):
        """
        Persistent request for a send in buffered mode.
        """
        prequest = _mpi.send_init(buf, dest, tag, self, 'B')
        return Prequest(prequest)

    def Ssend_init(self, buf, dest=0, tag=0):
        """
        Persistent request for a send in synchronous mode.
        """
        prequest = _mpi.send_init(buf, dest, tag, self, 'S')
        return Prequest(prequest)

    def Rsend_init(self, buf, dest=0, tag=0):
        """
        Persistent request for a send in ready mode.
        """
        prequest = _mpi.send_init(buf, dest, tag, self, 'R')
        return Prequest(prequest)

    # Collective Communications
    # -------------------------

    # Barrier Synchronization
    # -----------------------

    def Barrier(self):
        """
        Barrier synchronization.
        """
        _mpi.barrier(self)

    # Global Communication Functions
    # ------------------------------

    def Bcast(self, buf=None, root=0):
        """
        Broadcast a message from one process
        to all other processes in a group.
        """
        buf, fastmode = _mpi.make_buf(buf)
        if fastmode:
            _mpi.bcast(buf, root, self)
            return None
        else:
            serializer = self.SERIALIZER
            bcast = _mpi.bcast_pickled
            if _mpi.comm_test_inter(self):
                if root == _mpi.ROOT:
                    buf = serializer.dump(buf)
                else:
                    buf = None
            else:
                if root == _mpi.comm_rank(self):
                    buf = serializer.dump(buf)
                else:
                    buf = None
            buf = bcast(buf, root, self)
            if buf is not None:
                buf = serializer.load(buf)
            return buf

    def Gather(self, sendbuf, recvbuf=None, root=0):
        """
        Gather together values from a group of processes.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.gather(sendbuf, recvbuf, root, self)
            return None
        else:
            serializer = self.SERIALIZER
            gather = _mpi.gather_pickled
            if _mpi.comm_test_inter(self):
                if root != _mpi.ROOT and root != _mpi.PROC_NULL:
                    sendbuf = serializer.dump(sendbuf)
                else:
                    sendbuf = None
            else:
                sendbuf = serializer.dump(sendbuf)
            recvbuf = gather(sendbuf, recvbuf, root, self)
            if recvbuf is not None:
                recvbuf = map(serializer.load, recvbuf)
                recvbuf = list(recvbuf)
            return recvbuf

    def Gatherv(self, sendbuf, recvbuf, root=0):
        """
        Gather Vector, gather data to one process from all other
        processes in a group providing different amount of data and
        displacements at the receiving sides.
        """
        _mpi.gatherv(sendbuf, recvbuf, root, self)
        return None

    def Scatter(self, sendbuf=None, recvbuf=None, root=0):
        """
        Scatter Vector, scatter data from one process to all other
        processes in a group.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.scatter(sendbuf, recvbuf, root, self)
            return None
        else:
            serializer = self.SERIALIZER
            scatter = _mpi.scatter_pickled
            if _mpi.comm_test_inter(self):
                if root == _mpi.ROOT:
                    sendbuf = map(serializer.dump, sendbuf)
                    sendbuf = list(sendbuf)
                else:
                    sendbuf = None
            else:
                if root == _mpi.comm_rank(self):
                    sendbuf = map(serializer.dump, sendbuf)
                    sendbuf = list(sendbuf)
                else:
                    sendbuf = None
            recvbuf = scatter(sendbuf, recvbuf, root, self)
            if recvbuf is not None:
                recvbuf = serializer.load(recvbuf)
            return recvbuf

    def Scatterv(self, sendbuf, recvbuf, root=0):
        """
        Scatter data from one process to all other processes in a
        group providing different amount of data and displacements at
        the sending side.
        """
        _mpi.scatterv(sendbuf, recvbuf, root, self)
        return None

    def Allgather(self, sendbuf, recvbuf=None):
        """
        Gather to All, gather data from all processes
        and distribute it to all other processes in a group.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.allgather(sendbuf, recvbuf, self)
            return None
        else:
            serializer = self.SERIALIZER
            allgather = _mpi.allgather_pickled
            sendbuf = serializer.dump(sendbuf)
            recvbuf = allgather(sendbuf, recvbuf, self)
            recvbuf = map(serializer.load, recvbuf)
            recvbuf = list(recvbuf)
            return recvbuf

    def Allgatherv(self, sendbuf, recvbuf):
        """
        Gather to All Vector, gather data from all processes and
        distribute it to all other processes in a group providing
        different amount of data and displacements.
        """
        _mpi.allgatherv(sendbuf, recvbuf, self)
        return None

    def Alltoall(self, sendbuf, recvbuf=None):
        """
        All to All Scatter/Gather, send data from all to all
        processes in a group.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.alltoall(sendbuf, recvbuf, self)
            return None
        else:
            serializer = self.SERIALIZER
            alltoall = _mpi.alltoall_pickled
            sendbuf = map(serializer.dump, sendbuf)
            sendbuf = list(sendbuf)
            recvbuf = alltoall(sendbuf, recvbuf, self)
            recvbuf = map(serializer.load, recvbuf)
            recvbuf = list(recvbuf)
            return recvbuf

    def Alltoallv(self, sendbuf, recvbuf):
        """
        All to All Scatter/Gather Vector, send data from all to all
        processes in a group providing different amount of data and
        displacements.
        """
        _mpi.alltoallv(sendbuf, recvbuf, self)
        return None


    # Global Reduction Operations
    # ---------------------------

    def Reduce(self, sendbuf, recvbuf=None, op=SUM, root=0):
        """
        Reduce.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.reduce(sendbuf, recvbuf, op, root, self)
            return None
        else:
            # naive implementation
            recvbuf = self.Gather(sendbuf, None, root)
            if recvbuf is not None:
                if op in (MAXLOC, MINLOC):
                    recvbuf = zip(recvbuf, range(len(recvbuf)))
                recvbuf = _mpi._reduce(op, recvbuf)
            return recvbuf

    def Allreduce(self, sendbuf, recvbuf=None, op=SUM):
        """
        All Reduce.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.allreduce(sendbuf, recvbuf, op, self)
            return None
        else:
            # naive implementation
            serializer = self.SERIALIZER
            sendbuf = serializer.dump(sendbuf)
            recvbuf = _mpi.allgather_pickled(sendbuf, recvbuf, self)
            recvbuf = map(serializer.load, recvbuf)
            recvbuf = list(recvbuf)
            if op in (MAXLOC, MINLOC):
                recvbuf = zip(recvbuf, range(len(recvbuf)))
            recvbuf = _mpi._reduce(op, recvbuf)
            return recvbuf

    ## def Reduce_scatter(self, buff, op=SUM):
    ##     """
    ##     Reduce-Scatter. - Not implemented
    ##     """
    ##     raise NotImplementedError

    # Error handling
    # --------------

    def Get_errhandler(self):
        """
        Get the error handler for a communicator.
        """
        eh = _mpi.comm_get_errhandler(self)
        return Errhandler(eh)

    def Set_errhandler(self, errhandler):
        """
        Set the error handler for a communicator.
        """
        _mpi.comm_set_errhandler(self, errhandler)

    #

    def Abort(self, errorcode=0):
        """
        Terminate MPI execution environment.

        .. warning:: This is a direct call, use it with care!!!.
        """
        _mpi.comm_abort(self, errorcode)

    # Tests
    # -----

    def Is_inter(self):
        """
        Test to see if a comm is an intercommunicator.
        """
        return _mpi.comm_test_inter(self)

    def Is_intra(self):
        """
        Test to see if a comm is an intracommunicator.
        """
        return not _mpi.comm_test_inter(self)

    def Get_topology(self):
        """
        Determine the type of topology (if any) associated with a
        communicator.
        """
        return _mpi.topo_test(self)

    # Process Creation and Management
    # -------------------------------

    ## @staticmethod
    def Get_parent():
        """
        Return the parent intercommunicator for this process.
        """
        newcomm = _mpi.comm_get_parent()
        return Intercomm(newcomm)

    Get_parent = staticmethod(Get_parent)

    def Disconnect(self):
        """
        Disconnect from a communicator.

        .. note:: `self` will have a handle to ``MPI_COMM_NULL`` upon
           successful return.
        """
        _mpi.comm_disconnect(self)

    ## @staticmethod
    def Join(fd):
        """
        Create a intercommunicator by joining two processes
        connected by a socket
        """
        newcomm = _mpi.comm_join(fd)
        return Intercomm(newcomm)

    Join = staticmethod(Join)

    # Naming Objects
    # --------------

    def Get_name(self):
        """
        Get the print name from this communicator.
        """
        return _mpi.comm_get_name(self)

    def Set_name(self, name):
        """
        Set the print name for this communicator.
        """
        return _mpi.comm_set_name(self, name)

    # Port (OOMPI-like)
    # ----

    class Port(object):
        """Port (Communicator nested class)."""
        TAG = _mpi.TAG_UB-1
        def __init__(self, comm, pid):
            if pid < 0 or pid >= len(comm):
                raise ValueError('port number out of range')
            self._comm = comm
            self._pid  = pid
        def Send(self, buf, tag=0):
            """Send to port."""
            return self.comm.Send(buf, self.pid, tag)
        def Recv(self, buf=None, tag=0):
            """Receive from port."""
            return self.comm.Recv(buf, self.pid, tag)
        def Bcast(self, buf=None):
            """Broadcast from port."""
            return self.comm.Bcast(buf, self.pid)
        def Gather(self, sbuf, rbuf=None):
            """Gather to port."""
            return self.comm.Gather(sbuf, rbuf, self.pid)
        def Scatter(self, sbuf=None, rbuf=None):
            """Scatter from port."""
            return self.comm.Scatter(sbuf, rbuf, self.pid)
        def Reduce(self, sbuf, rbuf=None, op=SUM):
            """Reduce to port."""
            return self.comm.Reduce(sbuf, rbuf, op, self.pid)
        def __lshift__(self, stream):
            """Send sequence to port."""
            if type(stream) is not list:
                raise TypeError('input stream must be a list')
            self.Send(stream, self.TAG)
        def __rshift__(self, stream):
            """Receive sequence from port."""
            if type(stream) is not list:
                raise TypeError('output stream must be a list')
            stream.extend(self.Recv(None, self.TAG))
        comm = property(lambda self: self._comm,
                        doc='associated communicator')
        pid  = property(lambda self: self._pid,
                        doc='associated process rank')

    # Sequence Methods
    # ----------------

    def __len__(self):
        """
        Determine the number of ports of a communicator.
        """
        if self == _mpi.COMM_NULL:
            return 0
        elif _mpi.comm_test_inter(self):
            return _mpi.comm_remote_size(self)
        else:
            return _mpi.comm_size(self)

    def __getitem__(self, i):
        """
        Access the i'th port of a communicator.
        """
        if type(i) is not int:
            raise TypeError('indices must be integers')
        if i < 0:
            i += len(self)
        if i < 0 or i >= len(self):
            raise IndexError('index out of range')
        return self.__class__.Port(self, i)

    def __iter__(self):
        """
        Return an iterator.
        """
        i = 0
        port = self.__class__.Port
        while i < len(self):
            yield port(self, i)
            i += 1

    # Properties
    # ----------

    size = property(_mpi.comm_size,
                    doc='number of processes in group')
    rank = property(_mpi.comm_rank,
                    doc='rank of this process in group')

    is_inter = property(_mpi.comm_test_inter,
                        doc='True if is an intercommunicator')
    is_intra = property(_mpi.comm_test_intra,
                        doc='True if is an intracommunicator')
    topology = property(_mpi.topo_test,
                        doc='type of topology (if any)')

    name = property(_mpi.comm_get_name, _mpi.comm_set_name,
                    doc="communicator name")


# Predefined communicator handle
# ------------------------------

COMM_NULL = Comm(_mpi.COMM_NULL)
"""Null communicator handle"""


# --------------------------------------------------------------------
# Intracommunicator
# --------------------------------------------------------------------

class Intracomm(Comm):

    """
    Intracommunicator class.
    """

    def __init__(self, comm=None):
        Comm.__init__(self, comm)
        _mpi.comm_check_intra(self)

    # Communicator Constructors
    # -------------------------

    def Dup(self):
        """
        Duplicate intracommunicator.
        """
        newcomm = _mpi.comm_dup(self)
        return type(self)(newcomm)

    def Create(self, group):
        """
        Create intracommunicator from group.
        """
        newcomm = _mpi.comm_create(self, group)
        return type(self)(newcomm)

    def Split(self, color, key=0):
        """
        Split intracommunicator by color and key.
        """
        newcomm = _mpi.comm_split(self, color, key)
        return type(self)(newcomm)

    def Create_intercomm(self, local_leader,
                         peer_comm, remote_leader=0,
                         tag=0):
        """
        Create intercommunicator.
        """
        newcomm = _mpi.intercomm_create(self, local_leader,
                                        peer_comm, remote_leader,
                                        tag)
        return Intercomm(newcomm)

    def Create_cart(self, dims, periods=None, reorder=False):
        """
        Create cartesian communicator.
        """
        if periods is None:
            periods = [False] * len(dims)
        newcomm = _mpi.cart_create(self, dims, periods, reorder)
        return Cartcomm(newcomm)

    def Create_graph(self, index, edges, reorder=False):
        """
        Create graph communicator.
        """
        newcomm = _mpi.graph_create(self, index, edges, reorder)
        return Graphcomm(newcomm)


    # Global Reduction Operations
    # ---------------------------

    # Inclusive Scan

    def Scan(self, sendbuf, recvbuf=None, op=SUM):
        """
        Inclusive Scan.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.scan(sendbuf, recvbuf, op, self)
            return None
        else:
            # naive implementation
            recvbuf = self.Gather(sendbuf, root=0)
            if _mpi.comm_rank(self) == 0:
                if op in (MAXLOC, MINLOC):
                    recvbuf = zip(recvbuf, range(len(recvbuf)))
                    recvbuf = list(recvbuf)
                for i in range(1, len(recvbuf)):
                    recvbuf[i] = op(recvbuf[i-1], recvbuf[i])
            recvbuf = self.Scatter(recvbuf, root=0)
            return recvbuf

    # Exclusive Scan

    def Exscan(self, sendbuf, recvbuf=None, op=SUM):
        """
        Exclusive Scan.
        """
        sendbuf, sfastmode = _mpi.make_buf(sendbuf)
        recvbuf, rfastmode = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.exscan(sendbuf, recvbuf, op, self)
            return None
        else:
            # naive implementation
            recvbuf = self.Gather(sendbuf, root=0)
            if _mpi.comm_rank(self) == 0:
                if op in (MAXLOC, MINLOC):
                    recvbuf = zip(recvbuf, range(len(recvbuf)))
                    recvbuf = list(recvbuf)
                for i in range(1, len(recvbuf)):
                    recvbuf[i] = op(recvbuf[i-1], recvbuf[i])
                recvbuf.insert(0, None)
                recvbuf.pop(-1)
            recvbuf = self.Scatter(recvbuf, root=0)
            return recvbuf

    # Establishing Communication
    # --------------------------

    # Starting Processes

    def Spawn(self, command, args, maxprocs,
              info=None, root=0, errcodes=None):
        """
        Spawn instances of a single MPI application.
        """
        newcomm = _mpi.comm_spawn(command, args, maxprocs,
                                  info, root, self, errcodes)
        return Intercomm(newcomm)

    # Server Routines

    def Accept(self, port_name, info=None, root=0):
        """
        Accept a request to form a new intercommunicator.
        """
        newcomm = _mpi.comm_accept(port_name, info, root, self)
        return Intercomm(newcomm)

    # Client Routines

    def Connect(self, port_name, info=None, root=0):
        """
        Make a request to form a new intercommunicator.
        """
        newcomm = _mpi.comm_connect(port_name, info, root, self)
        return Intercomm(newcomm)


# Predefined communicator handles
# -------------------------------

COMM_SELF = Intracomm(_mpi.COMM_SELF_DUP)
"""Duplication of ``MPI_COMM_SELF`` handle"""
COMM_WORLD = Intracomm(_mpi.COMM_WORLD_DUP)
"""Duplication of ``MPI_COMM_WORLD`` handle"""

SELF = COMM_SELF
"""Convenience alias for `COMM_SELF`"""
WORLD = COMM_WORLD
"""Convenience alias for `COMM_WORLD`"""

__COMM_SELF__  = Intracomm(_mpi.COMM_SELF)
"""Actual handle to ``MPI_COMM_SELF``"""
__COMM_WORLD__ = Intracomm(_mpi.COMM_WORLD)
"""Actual handle to ``MPI_COMM_WORLD``"""



# --------------------------------------------------------------------
# Virtual Topologies
# --------------------------------------------------------------------


# Cartesian Topologies
# --------------------

# Cartesian Convenience Function

def Compute_dims(nnodes, dims):
    """
    Returns a balanced distribution of processes per coordinate
    direction.
    """
    return _mpi.dims_create(nnodes, dims)

class Cartcomm(Intracomm):

    """
    Cartesian topology class.
    """

    def __init__(self, comm=None):
        Intracomm.__init__(self, comm)
        _mpi.comm_check_cart(self)

    # Communicator Constructors
    # -------------------------

    def Dup(self):
        """
        Duplicate cartesian communicator.
        """
        newcomm = _mpi.comm_dup(self)
        return type(self)(newcomm)

    # Cartesian Inquiry Functions
    # ---------------------------

    def Get_dim(self):
        """
        Return number of dimensions.
        """
        return _mpi.cartdim_get(self)

    def Get_topo(self):
        """
        Return information on the cartesian topology.
        """
        return _mpi.cart_get(self)

    # Cartesian Translator Functions
    # ------------------------------

    def Get_cart_rank(self, coords):
        """
        Translate logical coordinates to ranks.
        """
        return _mpi.cart_rank(self, coords)

    def Get_coords(self, rank):
        """
        Translate ranks to logical coordinates.
        """
        return _mpi.cart_coords(self, rank)

    # Cartesian Shift Function
    # ------------------------

    def Shift(self, direction, disp):
        """
        Return a tuple (source,dest) of process ranks for data
        shifting with Comm.Sendrecv().
        """
        return _mpi.cart_shift(self, direction, disp)

    # Cartesian Partition Function
    # ----------------------------

    def Sub(self, remain_dims):
        """
        Return cartesian communicators that form lower-dimensional
        subgrids.
        """
        newcomm = _mpi.cart_sub(self, remain_dims)
        return type(self)(newcomm)

    # Cartesian Low-Level Functions
    # -----------------------------

    def Map(self, dims, periods):
        """
        Return an optimal placement for the calling process on the
        physical machine.
        """
        return _mpi.cart_map(self, dims, periods)

    # Properties
    # ----------

    dim  = property(_mpi.cartdim_get,
                    doc='number of dimensions')
    topo = property(_mpi.cart_get,
                    doc='Cartesian topology information')



# Graph Topologies
# ----------------

class Graphcomm(Intracomm):

    """
    Graph topology class.
    """

    def __init__(self, comm=None):
        Intracomm.__init__(self, comm)
        _mpi.comm_check_graph(self)

    # Communicator Constructors
    # -------------------------

    def Dup(self):
        """
        Duplicate graph communicator.
        """
        newcomm = _mpi.comm_dup(self)
        return type(self)(newcomm)

    # Graph Inquiry Functions
    # -----------------------

    def Get_dims(self):
        """
        Return the number of nodes and edges.
        """
        return _mpi.graphdims_get(self)

    def Get_topo(self):
        """
        Return index and edges.
        """
        return _mpi.graph_get(self)

    # Graph Information Functions
    # ---------------------------

    def Get_neighbors_count(self, rank):
        """
        Return number of neighbors of process.
        """
        return _mpi.graph_neigh_count(self, rank)

    def Get_neighbors(self, rank):
        """
        Return list of neighbors of process.
        """
        return _mpi.graph_neigh(self, rank)

    # Graph Low-Level Functions
    # -------------------------

    def Map(self, index, edges):
        """
        Return an optimal placement for the calling process on the
        physical machine.
        """
        return _mpi.graph_map(self, index, edges)

    # Properties
    # ----------

    dims = property(_mpi.graphdims_get,
                    doc='number of nodes and edges')
    topo = property(_mpi.graph_get,
                    doc='graph topology information')




# --------------------------------------------------------------------
# Intercommunicator
# --------------------------------------------------------------------

class Intercomm(Comm):

    """
    Intercommunicator class.
    """

    def __init__(self, comm=None):
        """
        Intercomm initializer.
        """
        Comm.__init__(self, comm)
        _mpi.comm_check_inter(self)

    # Intercommunicator Accessors
    # ---------------------------

    def Get_remote_size(self):
        """
        Intercommunicator remote size.
        """
        return _mpi.comm_remote_size(self)

    def Get_remote_group(self):
        """
        Access the remote group associated with the
        inter-communicator.
        """
        group = _mpi.comm_remote_group(self)
        return Group(group)

    # Intercommunicator Constructors
    # ------------------------------

    def Dup(self):
        """
        Duplicate intercommunicator.
        """
        newcomm = _mpi.comm_dup(self)
        return type(self)(newcomm)

    def Create(self, group):
        """
        Create intercommunicator from group.
        """
        newcomm = _mpi.comm_create(self, group)
        return type(self)(newcomm)

    def Split(self, color=0, key=0):
        """
        Split intercommunicator by color and key.
        """
        newcomm = _mpi.comm_split(self, color, key)
        return type(self)(newcomm)

    def Merge(self, high=False):
        """
        Merge intercommunicator.
        """
        intracomm = _mpi.intercomm_merge(self, high)
        return Intracomm(intracomm)

    # Properties
    # ----------

    remote_size = property(_mpi.comm_remote_size,
                           doc='size of remote group')



# --------------------------------------------------------------------
# [5] Process Creation and Management
# --------------------------------------------------------------------

# [5.4.2] Server Routines
# -----------------------

def Open_port(info=None):
    """
    Return an address that can be used to establish connections
    between groups of MPI processes.
    """
    return _mpi.open_port(info)

def Close_port(port_name):
    """
    Close a port.
    """
    return _mpi.close_port(port_name)

# [5.4.4] Name Publishing
# -----------------------

def Publish_name(service_name, info, port_name):
    """
    Publish a service name.
    """
    return _mpi.publish_name(service_name, info, port_name)

def Unpublish_name(service_name, info, port_name):
    """
    Unpublish a service name.
    """
    return _mpi.unpublish_name(service_name, info, port_name)

def Lookup_name(service_name, info=None):
    """
    Lookup a port name given a service name.
    """
    return _mpi.lookup_name(service_name, info)



# --------------------------------------------------------------------
# [6] One-Sided Communications
# --------------------------------------------------------------------

# Assertion modes
MODE_NOCHECK   = _mpi.MODE_NOCHECK
MODE_NOSTORE   = _mpi.MODE_NOSTORE
MODE_NOPUT     = _mpi.MODE_NOPUT
MODE_NOPRECEDE = _mpi.MODE_NOPRECEDE
MODE_NOSUCCEED = _mpi.MODE_NOSUCCEED

# Lock types
LOCK_EXCLUSIVE = _mpi.LOCK_EXCLUSIVE
LOCK_SHARED    = _mpi.LOCK_SHARED


class Win(_mpi.Win):

    """
    Window class.
    """

    def __init__(self, win=None):
        _mpi.Win.__init__(self, win)

    # [6.2] Initialization
    # --------------------

    # [6.2.1] Window Creation
    # -----------------------

    ## @classmethod
    def Create(cls, memory, disp_unit=1, info=None, comm=None):
        """
        Create an window object for one-sided communication.
        """
        assert comm is not None
        win = _mpi.win_create(memory, disp_unit, info, comm)
        return cls(win)

    Create = classmethod(Create)

    def Free(self):
        """
        Free a window.
        """
        return _mpi.win_free(self)

    # [6.2.2] Window Attributes
    # -------------------------

    def Get_group(self):
        """
        Return a duplicate of the group of the
        communicator used to create the window.
        """
        group = _mpi.win_get_group(self)
        return Group(group)

    # [6.3] Communication Calls
    # -------------------------

    # [6.3.1] Put
    # -----------

    def Put(self, origin, target_rank, target=None):
        """
        Put data into a memory window on a remote process.
        """
        return _mpi.win_put(origin, target_rank, target, self)

    # [6.3.2] Get
    # -----------

    def Get(self, origin, target_rank, target=None):
        """
        Get data from a memory window on a remote process.
        """
        return _mpi.win_get(origin, target_rank, target, self)

    # [6.3.4] Accumulate Functions
    # ----------------------------

    def Accumulate(self, origin, target_rank, target=None, op=SUM):
        """
        Accumulate data into the target process
        using remote memory access.
        """
        return _mpi.win_accumulate(origin, target_rank,
                                   target, op, self)

    # [6.4] Synchronization Calls
    # ---------------------------

    # [6.4.1] Fence
    # -------------

    def Fence(self, assertion=0):
        """
        Perform an MPI fence synchronization on a window.
        """
        return _mpi.win_fence(assertion, self)

    # [6.4.2] General Active Target Synchronization
    # ---------------------------------------------

    def Start(self, group, assertion=0):
        """
        Start an RMA access epoch for MPI.
        """
        return _mpi.win_start(group, assertion, self)

    def Complete(self):
        """
        Completes an RMA operations begun after an `Win.Start()`.
        """
        return _mpi.win_complete(self)

    def Post(self, group, assertion=0):
        """
        Start an RMA exposure epoch.
        """
        return _mpi.win_post(group, assertion, self)

    def Wait(self):
        """
        Complete an RMA exposure epoch begun with `Win.Post()`.
        """
        return _mpi.win_wait(self)

    def Test(self):
        """
        Test whether an RMA exposure epoch has completed.
        """
        return _mpi.win_test(self)

    # [6.4.3] Lock
    # ------------

    def Lock(self, lock_type, rank, assertion=0):
        """
        Begin an RMA access epoch at the target process.
        """
        return _mpi.win_lock(lock_type, rank, assertion, self)

    def Unlock(self, rank):
        """
        Complete an RMA access epoch at the target process.
        """
        return _mpi.win_unlock(rank, self)

    # [6.6] Error Handling
    # --------------------

    def Get_errhandler(self):
        """
        Get the error handler for a window.
        """
        eh = _mpi.win_get_errhandler(self)
        return Errhandler(eh)

    def Set_errhandler(self, errhandler):
        """
        Set the error handler for a window.
        """
        _mpi.win_set_errhandler(self, errhandler)

    # [8.4] Naming Objects
    # --------------------

    def Get_name(self):
        """
        Get the print name from a window.
        """
        return _mpi.win_get_name(self)

    def Set_name(self, name):
        """
        Set the print name for a window.
        """
        return _mpi.win_set_name(self, name)


    # Properties
    # ----------

    attrs  = property(_mpi.win_get_attrs,
                      doc="window attributes (base, size, disp_unit)")

    memory = property(_mpi.win_get_memory,
                      doc="window memory buffer")

    name = property(_mpi.win_get_name,
                    _mpi.win_set_name,
                    doc="window name")



# Predefined window handle

WIN_NULL = Win(_mpi.WIN_NULL)
"""Null window handle"""



# --------------------------------------------------------------------
# [9] I/O
# --------------------------------------------------------------------

# Opening modes

MODE_RDONLY          = _mpi.MODE_RDONLY
"""Read only"""
MODE_WRONLY          = _mpi.MODE_WRONLY
"""Write only"""
MODE_RDWR            = _mpi.MODE_RDWR
"""Reading and writing"""
MODE_CREATE          = _mpi.MODE_CREATE
"""Create the file if it does not exist"""
MODE_EXCL            = _mpi.MODE_EXCL
"""Error if creating file that already exists"""
MODE_DELETE_ON_CLOSE = _mpi.MODE_DELETE_ON_CLOSE
"""Delete file on close"""
MODE_UNIQUE_OPEN     = _mpi.MODE_UNIQUE_OPEN
"""File will not be concurrently opened elsewhere"""
MODE_SEQUENTIAL      = _mpi.MODE_SEQUENTIAL
"""File will only be accessed sequentially"""
MODE_APPEND          = _mpi.MODE_APPEND
"""Set initial position of all file pointers to end of file"""

# Positioning

SEEK_SET = _mpi.SEEK_SET
"""File pointer is set to offset"""
SEEK_CUR = _mpi.SEEK_CUR
"""File pointer is set to the current position plus offset"""
SEEK_END = _mpi.SEEK_END
"""File pointer is set to the end plus offset"""
DISPLACEMENT_CURRENT = _mpi.DISPLACEMENT_CURRENT
"""Special displacement value for files opened in sequential mode"""
DISP_CUR = DISPLACEMENT_CURRENT
"""Convenience alias for `DISPLACEMENT_CURRENT`"""


class File(_mpi.File):

    """
    File class.
    """

    def __init__(self, file=None):
        _mpi.File.__init__(self, file)

    # [9.2] File Manipulation
    # -----------------------

    # [9.2.1] Opening a File
    # ----------------------

    ## @classmethod
    def Open(cls, comm, filename, amode=None, info=None):
        """
        Open a file.
        """
        fh = _mpi.file_open(comm, filename, amode, info)
        return cls(fh)

    Open = classmethod(Open)

    # [9.2.2] Closing a File
    # ----------------------

    def Close(self):
        """
        Close a file.
        """
        _mpi.file_close(self)

    # [9.2.3] Deleting a File
    # -----------------------

    ## @staticmethod
    def Delete(filename, info=None):
        """
        Delete a file.
        """
        return _mpi.file_delete(filename, info)

    Delete = staticmethod(Delete)

    # [9.2.4] Resizing a File
    # -----------------------

    def Set_size(self, size):
        """
        Sets the file size.
        """
        return _mpi.file_set_size(self, size)

    # [9.2.5] Preallocating Space for a File
    # --------------------------------------

    def Preallocate(self, size):
        """
        Preallocate storage space for a file
        """
        return _mpi.file_preallocate(self, size)

    # [9.2.6] Querying the Size of a File
    # -----------------------------------
    def Get_size(self):
        """
        Return the file size.
        """
        return _mpi.file_get_size(self)

    # [9.2.7] Querying File Parameters
    # --------------------------------

    def Get_group(self):
        """
        Return the group of processes
        that opened the file.
        """
        group = _mpi.file_get_group(self)
        return Group(group)

    def Get_amode(self):
        """
        Return the file access mode.
        """
        return _mpi.file_get_amode(self)

    # [9.2.8] File Info
    # -----------------

    def Set_info(self, info):
        """
        Set new values for the hints
        associated with a file.
        """
        return _mpi.file_set_info(self, info)

    def Get_info(self):
        """
        Return the hints for a file that
        are actually being used by MPI.
        """
        info = _mpi.file_get_info(self)
        return Info(info)

    # [9.3] File Views
    # ----------------

    def Set_view(self, disp=0, etype=None,
                 filetype=None, datarep='native', info=None):
        """
        Set the file view.
        """
        if etype is None:
            etype = _mpi.BYTE
        if filetype is None:
            filetype = etype
        return _mpi.file_set_view(self, disp, etype,
                                  filetype, datarep, info)

    def Get_view(self):
        """
        Return the file view.
        """
        disp, etype, ftype, datarep = _mpi.file_get_view(self)
        return (disp, Datatype(etype), Datatype(ftype), datarep)

    # [9.4] Data Access
    # -----------------

    # [9.4.2] Data Access with Explicit Offsets
    # -----------------------------------------

    def Read_at(self, offset, buf, status=None):
        """
        Read using explicit offset.
        """
        return _mpi.file_read(self, offset, buf, status, 0) # 0: at

    def Read_at_all(self, offset, buf, status=None):
        """
        Collective read using explicit offset
        """
        return _mpi.file_read(self, offset, buf, status, 1) # 1: at_all

    def Write_at(self, offset, buf, status=None):
        """
        Write using explicit offset.
        """
        return _mpi.file_write(self, offset, buf, status, 0) # 0: at

    def Write_at_all(self, offset, buf, status=None):
        """
        Collective write using explicit offset
        """
        return _mpi.file_write(self, offset, buf, status, 1) # 1: at_all

    def Iread_at(self, offset, buf):
        """
        Nonblocking read using explicit offset.
        """
        request = _mpi.file_iread(self, offset, buf, 0) # 0: dummy
        return Request(request)

    def Iwrite_at(self, offset, buf):
        """
        Nonblocking write using explicit offset.
        """
        request = _mpi.file_iwrite(self, offset, buf, 0) # 0: dummy
        return Request(request)

    # [9.4.3] Data Access with Individual File Pointers
    # -------------------------------------------------

    def Read(self, buf, status=None):
        """
        Read using individual file pointer.
        """
        return _mpi.file_read(self, buf, status, 0) # 0: read

    def Read_all(self, buf, status=None):
        """
        Collective read using individual file pointer
        """
        return _mpi.file_read(self, buf, status, 1) # 1: read_all

    def Write(self, buf, status=None):
        """
        Write using individual file pointer.
        """
        return _mpi.file_write(self, buf, status, 0) # 0: write

    def Write_all(self, buf, status=None):
        """
        Collective write using individual file pointer
        """
        return _mpi.file_write(self, buf, status, 1) # 1: write_all

    def Iread(self, buf):
        """
        Nonblocking read using individual file pointer.
        """
        request = _mpi.file_iread(self, buf, 0) # 0: iread
        return Request(request)

    def Iwrite(self, buf):
        """
        Nonblocking write using individual file pointer.
        """
        request = _mpi.file_iwrite(self, buf, 0) # 0: iwrite
        return Request(request)

    def Seek(self, offset, whence=None):
        """
        Update the individual file pointer.
        """
        return _mpi.file_seek(self, offset, whence, 0) # 0: seek

    def Get_position(self):
        """
        Return the current position of the individual file pointer in
        etype units relative to the current view.
        """
        return _mpi.file_get_position(self, 0) # 0: get_pos

    def Get_byte_offset(self, offset):
        """
        Returns the absolute byte position in the file corresponding
        to 'offset' etypes relative to the current view.
        """
        return _mpi.file_get_byte_offset(self, offset)

    # [9.4.4] Data Access with Shared File Pointers
    # ---------------------------------------------

    def Read_shared(self, buf, status=None):
        """
        Read using shared file pointer.
        """
        return _mpi.file_read(self, buf, status, 2) # 2: read_shared

    def Write_shared(self, buf, status=None):
        """
        Write using shared file pointer.
        """
        return _mpi.file_write(self, buf, status, 2) # 2: write_shared

    def Iread_shared(self, buf):
        """
        Nonblocking read using shared file pointer.
        """
        request = _mpi.file_iread(self, buf, 2) # 2: iread_shared
        return Request(request)

    def Iwrite_shared(self, buf):
        """
        Nonblocking write using shared file pointer.
        """
        request = _mpi.file_iwrite(self, buf, 2) # 2: iwrite_shared
        return Request(request)

    def Read_ordered(self, buf, status=None):
        """
        Collective read using shared file pointer.
        """
        return _mpi.file_read(self, buf, status, 3) # 3: read_ordered

    def Write_ordered(self, buf, status=None):
        """
        Collective write using shared file pointer.
        """
        return _mpi.file_write(self, buf, status, 3) # 3: write_ordered

    def Seek_shared(self, offset, whence=None):
        """
        Update the shared file pointer.
        """
        return _mpi.file_seek(self, offset, whence, 2) # 2: seek_shared

    def Get_position_shared(self):
        """
        Return the current position of the shared file pointer in
        etype units relative to the current view.
        """
        return _mpi.file_get_position(self, 2) # 2: get_pos_shared

    # [9.4.5] Split Collective Data Access Routines
    # ---------------------------------------------

    ## _mpi.file_{read|write}_split(..., A, B) ->
    ## A: all(1)/ordered(3), B: begin(0)/end(1)

    # explicit offset

    def Read_at_all_begin(self, offset, buf):
        """
        Start a split collective read using explict offset.
        """
        return _mpi.file_read_split(self, offset, buf, None, 1, 0)

    def Read_at_all_end(self, buf, status=None):
        """
        Complete a split collective read using explict offset.
        """
        return _mpi.file_read_split(self, 0, buf, status, 1, 1)

    def Write_at_all_begin(self, offset, buf):
        """
        Start a split collective write using explict offset.
        """
        return _mpi.file_write_split(self, offset, buf, None, 1, 0)

    def Write_at_all_end(self, buf, status=None):
        """
        Complete a split collective write using explict offset.
        """
        return _mpi.file_write_split(self, 0, buf, status, 1, 1)

    # individual file pointer

    def Read_all_begin(self, buf):
        """
        Start a split collective read using individual file pointer.
        """
        return _mpi.file_read_split(self, buf, None, 1, 0)

    def Read_all_end(self, buf, status=None):
        """
        Complete a split collective read using individual file pointer.
        """
        return _mpi.file_read_split(self, buf, status, 1, 1)

    def Write_all_begin(self, buf):
        """
        Start a split collective write using individual file pointer.
        """
        return _mpi.file_write_split(self, buf, None, 1, 0)

    def Write_all_end(self, buf, status=None):
        """
        Complete a split collective write using individual file pointer.
        """
        return _mpi.file_write_split(self, buf, status, 1, 1)

    # shared file pointer

    def Read_ordered_begin(self, buf):
        """
        Start a split collective read using shared file pointer.
        """
        return _mpi.file_read_split(self, buf, None, 3, 0)

    def Read_ordered_end(self, buf, status=None):
        """
        Complete a split collective read using shared file pointer.
        """
        return _mpi.file_read_split(self, buf, status, 3, 1)

    def Write_ordered_begin(self, buf):
        """
        Start a split collective write using shared file pointer.
        """
        return _mpi.file_write_split(self, buf, None, 3, 0)

    def Write_ordered_end(self, buf, status=None):
        """
        Complete a split collective write using shared file pointer.
        """
        return _mpi.file_write_split(self, buf, status, 3, 1)

    # [9.5] File Interoperability
    # ---------------------------

    # [9.5.1] Datatypes for File Interoperability
    # -------------------------------------------

    def Get_type_extent(self, datatype):
        """
        Return the extent of datatype in the file.
        """
        return _mpi.file_get_type_extent(self, datatype)

    # [9.6] Consistency and Semantics
    # -------------------------------

    # [9.6.1] File Consistency
    # ------------------------

    def Set_atomicity(self, flag):
        """
        Set the atomicity mode
        """
        return _mpi.file_set_atomicity(self, flag)

    def Get_atomicity(self):
        """
        Return the atomicity mode
        """
        return _mpi.file_get_atomicity(self)


    def Sync(self):
        """
        Causes all previous writes to be transferred to the storage
        device.
        """
        return _mpi.file_sync(self)

    # [9.7] I/O Error Handling
    # ------------------------

    def Get_errhandler(self):
        """
        Get the error handler for a communicator.
        """
        eh = _mpi.file_get_errhandler(self)
        return Errhandler(eh)

    def Set_errhandler(self, errhandler):
        """
        Set the error handler for a communicator.
        """
        _mpi.file_set_errhandler(self, errhandler)

    # Properties
    # ----------

    size  = property(_mpi.file_get_size,
                     doc='file size, in bytes')
    amode = property(_mpi.file_get_amode,
                     doc='file access mode')


# Predefined file handle
# ----------------------

FILE_NULL = File(_mpi.FILE_NULL)
"""Null file handle"""


# --------------------------------------------------------------------
# Environmental Management
# --------------------------------------------------------------------

# Initialization and Exit

def Init():
    """
    Initialize the MPI execution environment.

    .. note:: ``MPI_INIT`` is actually called when this module is
       imported and only if MPI is not already initialized.
    """
    if getattr(Init, '__called', False):
        # this function was already called
        _func_info = (Init.__module__, Init.__name__)
        raise RuntimeError('%s.%s() already called' % _func_info)
    else:
        # initialization
        _mpi.init()
        _mpi._set_exception(Exception)
        # register this call
        setattr(Init, '__called', True)

def Finalize():
    """
    Terminate the MPI execution environment.

    .. note:: ``MPI_FINALIZE`` is actually called if this module had
       initialized MPI.

    .. warning:: ``COMM_WORLD`` and ``COMM_SELF`` will be freed if
       this function is called.
    """
    if getattr(Finalize, '__called', False):
        # this function was already called
        _func_info = (Finalize.__module__, Finalize.__name__)
        raise RuntimeError('%s.%s() already called' % _func_info)
    else:
        # finalization
        global COMM_SELF, COMM_WORLD
        COMM_SELF = COMM_WORLD = COMM_NULL
        _mpi.COMM_SELF = _mpi.COMM_WORLD = _mpi.COMM_NULL
        _mpi._set_exception(RuntimeError)
        _mpi.finalize()
        # register this call
        setattr(Finalize, '__called', True)

def Is_initialized():
    """
    Indicates whether ``MPI_INIT`` has been called.
    """
    return _mpi.initialized()

def Is_finalized():
    """
    Indicates whether ``MPI_FINALIZE`` has completed.

    .. note:: this function does not indicate whether ``MPI_INIT`` has
      been called.  It only indicates whether ``MPI_FINALIZE`` has been
      called.
    """
    return _mpi.finalized()

# Levels of MPI threading support.
THREAD_SINGLE = _mpi.THREAD_SINGLE
"""Only one thread will execute"""
THREAD_FUNNELED = _mpi.THREAD_FUNNELED
"""MPI calls are *funneled* to the main thread"""
THREAD_SERIALIZED = _mpi.THREAD_SERIALIZED
"""MPI calls are *serialized*"""
THREAD_MULTIPLE = _mpi.THREAD_MULTIPLE
"""Multiple threads may call MPI"""

def Init_thread(required):
    """
    Initialize the MPI execution environment.

    .. note:: ``MPI_INIT`` is actually called when this module is
       imported and only if MPI is not already initialized.
    """
    if getattr(Init_thread, '__called', False):
        # this function was already called
        _func = (Init_thread.__module__, Init_thread.__name__)
        raise RuntimeError('%s.%s() already called' % _func)
    else:
        # initialization
        provided = _mpi.init_thread(required)
        _mpi._set_exception(Exception)
        # register this call
        setattr(Init_thread, '__called', True)
        return provided

def Query_thread():
    """
    Return the level of thread support provided by the MPI library.
    """
    return _mpi.query_thread()

def Is_thread_main():
    """
    Indicate whether this thread called ``MPI_INIT`` or
    ``MPI_INIT_THREAD``.
    """
    return _mpi.is_thread_main()


# Implementation Information
# --------------------------

# MPI Version Number
# -----------------

def Get_version():
    """
    Obtain the version number of the MPI standard supported by the
    implementation as a tuple ``(version, subversion)``.
    """
    return _mpi.get_version()

# Environmental Inquires
# ----------------------

TAG_UB = _mpi.TAG_UB
"""Upper bound for *tag* values"""
HOST = _mpi.HOST
"""Rank of host process (if such exists)"""
IO = _mpi.IO
"""Rank of a process providing regular I/O facilities"""
WTIME_IS_GLOBAL = _mpi.WTIME_IS_GLOBAL
"""Indicate whether clocks are synchronized"""
UNIVERSE_SIZE = _mpi.UNIVERSE_SIZE
"""Indicate how many processes can usefully be started
on the underlying MPI runtime environment"""
APPNUM = _mpi.APPNUM
"""Indicate if a process was spawned"""

def Get_processor_name():
    """
    Obtain the name of the calling processor.
    """
    return _mpi.get_processor_name()

# Timers and Synchronization
# --------------------------

def Wtime():
    """
    Return an elapsed time on the calling processor.

    .. note:: This is intended to be a high-resolution, elapsed (or
       wall) clock.  Use `Wtick` to determine the resolution of
       `Wtime` . If the attribute `WTIME_IS_GLOBAL` is ``True``, then
       the value is synchronized across all processes in `COMM_WORLD`.
    """
    return _mpi.wtime()

def Wtick():
    """
    Return the resolution of ``Wtime``.
    """
    return _mpi.wtick()

# Maximum string sizes

MAX_PROCESSOR_NAME = _mpi.MAX_PROCESSOR_NAME
MAX_ERROR_STRING   = _mpi.MAX_ERROR_STRING
MAX_PORT_NAME      = _mpi.MAX_PORT_NAME
MAX_INFO_KEY       = _mpi.MAX_INFO_KEY
MAX_INFO_VAL       = _mpi.MAX_INFO_VAL
MAX_OBJECT_NAME    = _mpi.MAX_OBJECT_NAME
MAX_DATAREP_STRING = _mpi.MAX_DATAREP_STRING

# Error Handling
# --------------

class Errhandler(_mpi.Errhandler):

    """
    Errhandler class.
    """

    def __init__(self, errhandler=None):
        _mpi.Errhandler.__init__(self, errhandler)

    def Free(self):
        """
        Free an error handler.
        """
        _mpi.errhandler_free(self)

# Predefined error handlers

ERRHANDLER_NULL = Errhandler(_mpi.ERRHANDLER_NULL)
"""Null error handler"""
ERRORS_ARE_FATAL = Errhandler(_mpi.ERRORS_ARE_FATAL)
"""Errors are fatal (this usually abort execution)"""
ERRORS_RETURN = Errhandler(_mpi.ERRORS_RETURN)
"""Errors are ignored (just return error code)"""

# Exception class

class Exception(RuntimeError):

    """
    Exception class.
    """

    def __init__(self, ierr, *args):
        self.__ierr = _mpi.SUCCESS
        self.__ierr = int(ierr)
        RuntimeError.__init__(self, int(self), *args)

    def __int__(self):
        return self.__ierr

    def __str__(self):
        return _mpi.error_string(int(self))

    def __eq__(self, error):
        if isinstance(error, Exception):
            error = int(error)
        return int(self) == error

    def __ne__(self, error):
        if isinstance(error, Exception):
            error = int(error)
        return int(self) != error

    def Get_error_code(self):
        """Error code."""
        return int(self)

    def Get_error_class(self):
        """Error class."""
        return _mpi.error_class(int(self))

    def Get_error_string(self):
        """Error string."""
        return _mpi.error_string(int(self))

    # Properties
    # ----------

    error_code   = property(Get_error_code,   doc='error code')
    error_class  = property(Get_error_class,  doc='error class')
    error_string = property(Get_error_string, doc='error string')


def Get_error_class(errorcode):
    """
    Converts an error code into an error class.
    """
    return _mpi.error_class(errorcode)

def Get_error_string(errorcode):
    """
    Returns a string for a given error code.
    """
    return _mpi.error_string(errorcode)


# Predefined error classes
# ------------------------

SUCCESS = _mpi.SUCCESS

ERR_BUFFER    = _mpi.ERR_BUFFER
ERR_COUNT     = _mpi.ERR_COUNT
ERR_TYPE      = _mpi.ERR_TYPE
ERR_TAG       = _mpi.ERR_TAG
ERR_COMM      = _mpi.ERR_COMM
ERR_RANK      = _mpi.ERR_RANK
ERR_ROOT      = _mpi.ERR_ROOT
ERR_TRUNCATE  = _mpi.ERR_TRUNCATE
ERR_IN_STATUS = _mpi.ERR_IN_STATUS
ERR_PENDING   = _mpi.ERR_PENDING

ERR_GROUP   = _mpi.ERR_GROUP
ERR_OP      = _mpi.ERR_OP
ERR_REQUEST = _mpi.ERR_REQUEST

ERR_DIMS     = _mpi.ERR_DIMS
ERR_TOPOLOGY = _mpi.ERR_TOPOLOGY

ERR_ARG     = _mpi.ERR_ARG
ERR_INTERN  = _mpi.ERR_INTERN
ERR_OTHER   = _mpi.ERR_OTHER
ERR_UNKNOWN = _mpi.ERR_UNKNOWN

ERR_KEYVAL = _mpi.ERR_KEYVAL

ERR_NO_MEM  = _mpi.ERR_NO_MEM

ERR_NAME    = _mpi.ERR_NAME
ERR_PORT    = _mpi.ERR_PORT
ERR_SERVICE = _mpi.ERR_SERVICE
ERR_SPAWN   = _mpi.ERR_SPAWN

ERR_INFO       = _mpi.ERR_INFO
ERR_INFO_KEY   = _mpi.ERR_INFO_KEY
ERR_INFO_VALUE = _mpi.ERR_INFO_VALUE
ERR_INFO_NOKEY = _mpi.ERR_INFO_NOKEY

ERR_WIN           = _mpi.ERR_WIN
ERR_BASE          = _mpi.ERR_BASE
ERR_SIZE          = _mpi.ERR_SIZE
ERR_DISP          = _mpi.ERR_DISP
ERR_LOCKTYPE      = _mpi.ERR_LOCKTYPE
ERR_ASSERT        = _mpi.ERR_ASSERT
ERR_RMA_CONFLICT  = _mpi.ERR_RMA_CONFLICT
ERR_RMA_SYNC      = _mpi.ERR_RMA_SYNC

ERR_FILE                  = _mpi.ERR_FILE
ERR_NOT_SAME              = _mpi.ERR_NOT_SAME
ERR_AMODE                 = _mpi.ERR_AMODE
ERR_UNSUPPORTED_DATAREP   = _mpi.ERR_UNSUPPORTED_DATAREP
ERR_UNSUPPORTED_OPERATION = _mpi.ERR_UNSUPPORTED_OPERATION
ERR_NO_SUCH_FILE          = _mpi.ERR_NO_SUCH_FILE
ERR_FILE_EXISTS           = _mpi.ERR_FILE_EXISTS
ERR_BAD_FILE              = _mpi.ERR_BAD_FILE
ERR_ACCESS                = _mpi.ERR_ACCESS
ERR_NO_SPACE              = _mpi.ERR_NO_SPACE
ERR_QUOTA                 = _mpi.ERR_QUOTA
ERR_READ_ONLY             = _mpi.ERR_READ_ONLY
ERR_FILE_IN_USE           = _mpi.ERR_FILE_IN_USE
ERR_DUP_DATAREP           = _mpi.ERR_DUP_DATAREP
ERR_CONVERSION            = _mpi.ERR_CONVERSION
ERR_IO                    = _mpi.ERR_IO

ERR_LASTCODE = _mpi.ERR_LASTCODE


# Convenience constants
# ---------------------

WORLD_SIZE = _mpi.WORLD_SIZE
"""*size* of `COMM_WORLD`, shortcut for ``COMM_WORLD.Get_size()``."""
WORLD_RANK = _mpi.WORLD_RANK
"""*rank* in `COMM_WORLD`, shortcut for ``COMM_WORLD.Get_rank()``."""



# --------------------------------------------------------------------
# SWIG support
# --------------------------------------------------------------------

def SWIG(cls):
    "Adds SWIG support to MPI Types"
    try:
        import mpi4py._mpi_swig as _swig
        _as   = getattr(_swig, 'as_'   + cls.__name__)
        _from = getattr(_swig, 'from_' + cls.__name__)
        def As_swig(self):
            """Access the object as a *SWIG pointer*."""
            return _as(self)
        def From_swig(cls, obj):
            """Constructs an object from a *SWIG pointer*."""
            return cls(_from(obj))
    except ImportError:
        _swig = None
        def As_swig(self):
            """Access the object as a *SWIG pointer*."""
            raise ImportError('SWIG support not available')
        def From_swig(cls, obj):
            """Constructs an object from a *SWIG pointer*."""
            raise ImportError('SWIG support not available')
    cls.As_swig = As_swig
    cls.From_swig = classmethod(From_swig)
    cls.this = property(As_swig, doc='SWIG handle')
    cls.thisown = property(lambda self: 0, doc='SWIG handle ownership')
    del _swig, As_swig, From_swig

for klass in (Datatype, Status, Request, Op, Info,
              Group, Comm, Win, File, Errhandler):
    SWIG(klass)
del SWIG, klass


# --------------------------------------------------------------------
# Module initialization
# --------------------------------------------------------------------

ExceptionMPI = Exception
__all__ = [sym for sym in dir() if not sym.startswith('_')]
__all__.remove('Exception')
sym = None
del sym

def _mpi_init():
    """Initialize _mpi module"""
    try:
        _mpi._set_exception(Exception)
    except StandardError:
        pass
_mpi_init()
del _mpi_init

def _mpi_fini():
    """Finalize _mpi module"""
    try:
        _mpi._del_exception()
    except StandardError:
        pass
    try:
        if not _mpi.initialized():
            return
        if _mpi.finalized():
            return
    except StandardError:
        return
import atexit
atexit.register(_mpi_fini)
del atexit, _mpi_fini



# --------------------------------------------------------------------
# Misc utils (some may go away in future releases)
# --------------------------------------------------------------------

def _mpi_info():
    """
    Return string ``name`` and integer 3-tuple ``version``
    of the underlying MPI implementation.
    """
    return _mpi._mpi_info()

def _distribute(N, B, i):
    """
    Compute interval [low, high) in bin i
    when sequence of N elements has to be
    distributed over B bins.
    """
    return _mpi.distribute(N, B, i)

def _pprint(message=None, comm=None, root=0):
    """
    Synchronized print.
    """
    import sys
    if comm is None:
        comm = COMM_WORLD
    inbuf  = comm.SERIALIZER.dump(message)
    result = _mpi.gather_pickled(inbuf, None, root, comm)
    if comm.Get_rank() == root:
        for i in result:
            msg = comm.SERIALIZER.load(i)
            sys.stdout.write(str(msg)+'\n')
            sys.stdout.flush()
    return

def _rprint(message=None, comm=None, root=0):
    """
    Rooted print.
    """
    import sys
    if comm is None:
        comm = COMM_WORLD
    if comm.Get_rank() == root:
        sys.stdout.write(str(message)+'\n')
        sys.stdout.flush()
    return
