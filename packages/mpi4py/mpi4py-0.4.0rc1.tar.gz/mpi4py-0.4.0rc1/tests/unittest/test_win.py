import unittest
from mpi4py import MPI

typemap = dict(h=MPI.SHORT,
               i=MPI.INT,
               l=MPI.LONG,
               f=MPI.FLOAT,
               d=MPI.DOUBLE)

arrayimpl = []

try:
    import array
    def mk_dtype_array(a, datatype):
        return datatype or typemap[a.typecode]
    def mk_buf_array_1(a, dt=None, c=None):
        return MPI.Buffer(a, c or len(a), mk_dtype_array(a, dt))
    def mk_buf_array_2(a, dt=None, c=None):
        bptr, blen = a.buffer_info()
        return MPI.Buffer((bptr, False), c or blen, mk_dtype_array(a, dt))
    mk_buf_array = (mk_buf_array_1, mk_buf_array_2)
    mk_arr_array = lambda typecode, init: array.array(typecode, init)
    eq_arr_array = lambda a, b : a == b
    arrayimpl.append((mk_buf_array, mk_arr_array, eq_arr_array))
except ImportError:
    pass

try:
    import numpy
    def mk_dtype_numpy(a, datatype):
        return datatype or typemap[a.dtype.char]
    def mk_buf_numpy_1(a, dt=None, c=None):
        return MPI.Buffer(a, c or a.size, mk_dtype_numpy(a, dt))
    def mk_buf_numpy_2(a, dt=None, c=None):
        return MPI.Buffer(a.data, c or a.size, mk_dtype_numpy(a, dt))
    def mk_buf_numpy_3(a, dt=None, c=None):
        data = a.__array_interface__['data']
        return MPI.Buffer(data, c or a.size, mk_dtype_numpy(a, dt))
    mk_buf_numpy = (mk_buf_numpy_1, mk_buf_numpy_2, mk_buf_numpy_3)
    mk_arr_numpy = lambda typecode, init: numpy.array(init, dtype=typecode)
    eq_arr_numpy = lambda a, b : numpy.allclose(a, b)
    arrayimpl.append((mk_buf_numpy, mk_arr_numpy, eq_arr_numpy))
except ImportError:
    pass

class TestWinBase(object):
    
    COMM = MPI.COMM_NULL
    
    def setUp(self):
        self.memory = None
        self.WIN = None
        try:
            self.memory = MPI.Alloc_mem(100*MPI.DOUBLE.size)
            self.size = len(self.memory)
            self.base = MPI.Get_address(self.memory)
            self.disp = 1
            self.COMM = MPI.COMM_WORLD
            self.info = MPI.INFO_NULL
            self.WIN = MPI.Win.Create(self.memory, self.disp,
                                      self.info, self.COMM)
        except NotImplementedError:
            if self.memory is not None:
                MPI.Free_mem(self.memory)
            self.WIN = None
        
    def tearDown(self):
        if self.WIN is None: return
        self.WIN.Free()
        MPI.Free_mem(self.memory)

    def testGetSetName(self):
        if self.WIN is None: return
        try:
            name = self.WIN.Get_name()
            self.WIN.Set_name('win')
            self.assertEqual(self.WIN.Get_name(), 'win')
            self.WIN.Set_name(name)
            self.assertEqual(self.WIN.Get_name(), name)
        except NotImplementedError:
            pass

    def testWinGetSetErrhandler(self):
        if self.WIN is None: return
        set_null_eh = lambda : self.WIN.Set_errhandler(MPI.ERRHANDLER_NULL)
        self.assertRaises(MPI.Exception, set_null_eh)
        for ERRHANDLER in [MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,
                           MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,]:
            errhdl_1 = self.WIN.Get_errhandler()
            self.assertNotEqual(errhdl_1, MPI.ERRHANDLER_NULL)
            self.WIN.Set_errhandler(ERRHANDLER)
            errhdl_2 = self.WIN.Get_errhandler()
            self.assertEqual(errhdl_2, ERRHANDLER)
            errhdl_2.Free()
            self.assertEqual(errhdl_2, MPI.ERRHANDLER_NULL)
            #continue
            self.WIN.Set_errhandler(errhdl_1)
            errhdl_1.Free()
            self.assertEqual(errhdl_1, MPI.ERRHANDLER_NULL)

    def testProperties(self):
        if self.WIN is None: return
        #
        self.assertEqual(self.WIN.base,      self.base)
        self.assertEqual(self.WIN.size,      self.size)
        self.assertEqual(self.WIN.disp_unit, self.disp)
        #
        cgroup = self.COMM.Get_group()
        wgroup = self.WIN.Get_group()
        rescmp = MPI.Group.Compare(cgroup, wgroup)
        self.assertEqual(rescmp, MPI.IDENT)
        cgroup.Free()
        wgroup.Free()

    def testFence(self):
        if self.WIN is None: return
        self.WIN.Fence()
        assertion = 0
        modes = [0,
                 MPI.MODE_NOSTORE,
                 MPI.MODE_NOPUT,
                 MPI.MODE_NOPRECEDE,
                 MPI.MODE_NOSUCCEED]
        for mode in modes:
            self.WIN.Fence(mode)
            assertion |= mode
            self.WIN.Fence(assertion)
        
##     def testPutGet(self):
##         if self.WIN is None: return
##         group = self.WIN.Get_group()
##         size = group.Get_size()
##         group.Free()
##         for mkbufs, array, equal in arrayimpl:
##             for mkbuf in mkbufs:
##                 for typecode, datatype in typemap.iteritems():
##                     for count in xrange(1, 10):
##                         for rank in xrange(size):
##                             sbuf = array(typecode, xrange(count))
##                             rbuf = array(typecode, [-1] * (count+1))
##                             self.WIN.Put(mkbuf(sbuf, datatype, count), rank)
##                             self.WIN.Fence()
##                             self.WIN.Get(mkbuf(rbuf, datatype, count), rank)
##                             self.WIN.Fence()
##                             for i, value in enumerate(rbuf[:-1]):
##                                 self.assertEqual(value, i)
##                             self.assertEqual(rbuf[-1], -1)

    
class TestWinSelf(TestWinBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestWinWorld(TestWinBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

        

if __name__ == '__main__':
    #unittest.main()
    try:
        unittest.main()
    except SystemExit:
        pass
