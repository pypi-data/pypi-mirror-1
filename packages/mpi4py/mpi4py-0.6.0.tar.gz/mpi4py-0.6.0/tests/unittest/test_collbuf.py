import unittest
from mpi4py import MPI
from array import array

typemap = dict(#b=MPI.SIGNED_CHAR,
               h=MPI.SHORT,
               i=MPI.INT,
               l=MPI.LONG,
               f=MPI.FLOAT,
               d=MPI.DOUBLE)

arrayimpl = []

try:
    import array
    def mk_dtype_array(a, datatype):
        return datatype or typemap[a.typecode]
    def mk_buf_array_1(a, dt=None, s=1, c=None):
        return MPI.Buffer(a, (c or len(a))//s, mk_dtype_array(a, dt))
    def mk_buf_array_2(a, dt=None, s=1, c=None):
        bptr, blen = a.buffer_info()
        return MPI.Buffer((bptr, False), (c or blen)//s, mk_dtype_array(a, dt))
    def mk_buf_array_3(a, dt=None, s=1, c=None):
        return (a, (c or len(a))//s, mk_dtype_array(a, dt))
    def mk_buf_array_4(a, dt=None, s=1, c=None):
        bptr, blen = a.buffer_info()
        return [(bptr, False), (c or blen)//s, mk_dtype_array(a, dt)]
    mk_buf_array = (mk_buf_array_1, mk_buf_array_2,
                    mk_buf_array_3, mk_buf_array_4)
    mk_arr_array = lambda typecode, init: array.array(typecode, init)
    eq_arr_array = lambda a, b : a == b
    arrayimpl.append((mk_buf_array, mk_arr_array, eq_arr_array))
except ImportError:
    pass

try:
    import numpy
    def mk_dtype_numpy(a, datatype):
        return datatype or typemap[a.dtype.char]
    def mk_buf_numpy_1(a, dt=None, s=1, c=None):
        return MPI.Buffer(a, (c or a.size)//s, mk_dtype_numpy(a, dt))
    def mk_buf_numpy_2(a, dt=None, s=1, c=None):
        return MPI.Buffer(a.data, (c or a.size)//s, mk_dtype_numpy(a, dt))
    def mk_buf_numpy_3(a, dt=None, s=1, c=None):
        data = a.__array_interface__['data']
        return MPI.Buffer(data,  (c or a.size)//s, mk_dtype_numpy(a, dt))
    def mk_buf_numpy_4(a, dt=None, s=1, c=None):
        return (a,  (c or a.size)//s, mk_dtype_numpy(a, dt))
    def mk_buf_numpy_5(a, dt=None, s=1, c=None):
        return (a.data, (c or a.size)//s, mk_dtype_numpy(a, dt))
    def mk_buf_numpy_6(a, dt=None, s=1, c=None):
        data = a.__array_interface__['data']
        return (data,  (c or a.size)//s, mk_dtype_numpy(a, dt))
    mk_buf_numpy = (mk_buf_numpy_1, mk_buf_numpy_2, mk_buf_numpy_3,
                    mk_buf_numpy_4, mk_buf_numpy_5, mk_buf_numpy_6,
                    )
    mk_arr_numpy = lambda typecode, init: numpy.array(init, dtype=typecode)
    eq_arr_numpy = lambda a, b : numpy.allclose(a, b)
    arrayimpl.append((mk_buf_numpy, mk_arr_numpy, eq_arr_numpy))
except ImportError:
    pass


def maxvalue(a):
    try:
        typecode = a.typecode
    except AttributeError:
        typecode = a.dtype.char
    if typecode == ('f'):
        return 1e30
    elif typecode == ('d'):
        return 1e300
    else:
        return 2 ** (a.itemsize * 7) - 1


class TestCollBufBase(object):

    COMM = MPI.COMM_NULL

    def testBarrier(self):
        self.COMM.Barrier()

    def testBcast(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        if rank == root:
                            buf = array(typecode, [root]*root)
                        else:
                            buf = array(typecode, [-1]*root)
                        self.COMM.Bcast(mkbuf(buf, datatype), root=root)
                        for value in buf:
                            self.assertEqual(value, root)

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        sbuf = array(typecode, [root]*root)
                        if rank == root:
                            rbuf = array(typecode, [-1]*(len(sbuf)*size))
                        else:
                            rbuf = array(typecode, [])
                        self.COMM.Gather(mkbuf(sbuf, datatype),
                                         mkbuf(rbuf, datatype, size),
                                         root=root)
                        if rank == root:
                            for value in rbuf:
                                self.assertEqual(value, root)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        rbuf = array(typecode, [-1]*size)
                        if rank == root:
                            sbuf = array(typecode, [root]*(len(rbuf)*size))
                        else:
                            sbuf = array(typecode, [])
                        self.COMM.Scatter(mkbuf(sbuf, datatype, size),
                                          mkbuf(rbuf, datatype),
                                          root=root)
                        for value in rbuf:
                            self.assertEqual(value, root)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        sbuf = array(typecode, [root]*root)
                        rbuf = array(typecode, [-1]*(len(sbuf)*size))
                        self.COMM.Allgather(mkbuf(sbuf, datatype),
                                            mkbuf(rbuf, datatype, size))
                        for value in rbuf:
                            self.assertEqual(value, root)

    def testAlltoall(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        sbuf = array(typecode, [root]*(root*size))
                        rbuf = array(typecode, [-1]*(root*size))
                        self.COMM.Alltoall(mkbuf(sbuf, datatype, size),
                                           mkbuf(rbuf, datatype, size))
                        for value in rbuf:
                            self.assertEqual(value, root)

    def assertAlmostEqual(self, first, second):
        num = float(float(second-first))
        den = float(second+first)/2 or 1.0
        if (abs(num/den) > 1e-2):
            raise self.failureException('%r != %r' % (first, second))

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                            sbuf = array(typecode, range(size))
                            rbuf = array(typecode, [-1]*len(sbuf))
                            self.COMM.Reduce(mkbuf(sbuf, datatype),
                                             mkbuf(rbuf, datatype),
                                             op, root)
                            max_val = maxvalue(rbuf)
                            for i, value in enumerate(rbuf):
                                if rank != root:
                                    self.assertEqual(value, -1)
                                    continue
                                if op == MPI.SUM:
                                    if (i * size) < max_val:
                                        self.assertAlmostEqual(value, i*size)
                                elif op == MPI.PROD:
                                    if (i ** size) < max_val:
                                        self.assertAlmostEqual(value, i**size)
                                elif op == MPI.MAX:
                                    self.assertEqual(value, i)
                                elif op == MPI.MIN:
                                    self.assertEqual(value, i)

    def testAllreduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                        sbuf = array(typecode, range(size))
                        rbuf = array(typecode, [0]*size)
                        self.COMM.Allreduce(mkbuf(sbuf, datatype),
                                            mkbuf(rbuf, datatype),
                                            op)
                        max_val = maxvalue(rbuf)
                        for i, value in enumerate(rbuf):
                            if op == MPI.SUM:
                                if (i * size) < max_val:
                                    self.assertAlmostEqual(value, i*size)
                            elif op == MPI.PROD:
                                if (i ** size) < max_val:
                                    self.assertAlmostEqual(value, i**size)
                            elif op == MPI.MAX:
                                self.assertEqual(value, i)
                            elif op == MPI.MIN:
                                self.assertEqual(value, i)


    def testScan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        # --
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                        sbuf = array(typecode, range(size))
                        rbuf = array(typecode, [0]*size)
                        self.COMM.Scan(mkbuf(sbuf, datatype),
                                       mkbuf(rbuf, datatype),
                                       op)
                        max_val = maxvalue(rbuf)
                        for i, value in enumerate(rbuf):
                            if op == MPI.SUM:
                                if (i * (rank + 1)) < max_val:
                                    self.assertAlmostEqual(value, i * (rank + 1))
                            elif op == MPI.PROD:
                                if (i ** (rank + 1)) < max_val:
                                    self.assertAlmostEqual(value, i ** (rank + 1))
                            elif op == MPI.MAX:
                                self.assertEqual(value, i)
                            elif op == MPI.MIN:
                                self.assertEqual(value, i)

    def testExscan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                        sbuf = array(typecode, range(size))
                        rbuf = array(typecode, [0]*size)
                        try:
                            self.COMM.Exscan(mkbuf(sbuf, datatype),
                                             mkbuf(rbuf, datatype),
                                             op)
                        except NotImplementedError:
                            return
                        if rank == 1:
                            for i, value in enumerate(rbuf):
                                self.assertEqual(value, i)
                        elif rank > 1:
                            max_val = maxvalue(rbuf)
                            for i, value in enumerate(rbuf):
                                if op == MPI.SUM:
                                    if (i * rank) < max_val:
                                        self.assertAlmostEqual(value, i * rank)
                                elif op == MPI.PROD:
                                    if (i ** rank) < max_val:
                                        self.assertAlmostEqual(value, i ** rank)
                                elif op == MPI.MAX:
                                    self.assertEqual(value, i)
                                elif op == MPI.MIN:
                                    self.assertEqual(value, i)


    def testBcastTypeIndexed(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for root in range(size):
                    for typecode, datatype in typemap.items():
                        #
                        if rank == root:
                            buf = array(typecode, range(10))
                        else:
                            buf = array(typecode, [-1]*10)
                        indices = range(0, len(buf), 2)
                        newtype = datatype.Create_indexed(1, indices)
                        newtype.Commit()
                        self.COMM.Bcast(mkbuf(buf, newtype, 1, 1), root=root)
                        newtype.Free()
                        if rank != root:
                            for i, value in enumerate(buf):
                                if (i % 2):
                                    self.assertEqual(value, -1)
                                else:
                                    self.assertEqual(value, i)

                        #
                        if rank == root:
                            buf = array(typecode, range(10))
                        else:
                            buf = array(typecode, [-1]*10)
                        indices = range(1, len(buf), 2)
                        newtype = datatype.Create_indexed(1, indices)
                        newtype.Commit()
                        self.COMM.Bcast(mkbuf(buf, newtype, 1, 1), root)
                        newtype.Free()
                        if rank != root:
                            for i, value in enumerate(buf):
                                if not (i % 2):
                                    self.assertEqual(value, -1)
                                else:
                                    self.assertEqual(value, i)


class TestCollBufInplaceBase(object):

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        count = root+3
                        if rank == root:
                            sbuf = MPI.IN_PLACE
                            buf = array(typecode, [-1]*(size*count))
                            buf[(rank*count):((rank+1)*count)] = array(typecode, [root] * count)
                            rbuf = mkbuf(buf, datatype, size)
                        else:
                            buf = array(typecode, [root]*count)
                            sbuf = mkbuf(buf, datatype)
                            rbuf = None
                        try:
                            self.COMM.Gather(sbuf, rbuf, root=root)
                        except NotImplementedError:
                            return
                        for value in buf:
                            self.assertEqual(value, root)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        for count in range(1, 10):
                            if rank == root:
                                buf = array(typecode, [root]*(size*count))
                                sbuf = mkbuf(buf, datatype, size)
                                rbuf = MPI.IN_PLACE
                            else:
                                buf = array(typecode, [-1]*count)
                                sbuf = None
                                rbuf = mkbuf(buf, datatype)
                            try:
                                self.COMM.Scatter(sbuf, rbuf, root=root)
                            except NotImplementedError:
                                return
                            for value in buf:
                                self.assertEqual(value, root)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for count in range(1, 10):
                        buf = array(typecode, [-1]*(count*size))
                        buf[(rank*count):((rank+1)*count)] = array(typecode, [count] * count)
                        try:
                            self.COMM.Allgather(MPI.IN_PLACE, mkbuf(buf, datatype, size))
                        except NotImplementedError:
                            return
                        for value in buf:
                            self.assertEqual(value, count)

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                            count = size
                            if rank == root:
                                buf  = array(typecode, range(size))
                                sbuf = MPI.IN_PLACE
                                rbuf = mkbuf(buf, datatype)
                            else:
                                buf  = array(typecode, range(size))
                                buf2 = array(typecode, range(size))
                                sbuf = mkbuf(buf, datatype)
                                rbuf = mkbuf(buf2, datatype)
                            try:
                                self.COMM.Reduce(sbuf, rbuf, op, root)
                            except NotImplementedError:
                                return
                            if rank == root:
                                max_val = maxvalue(buf)
                                for i, value in enumerate(buf):
                                    if op == MPI.SUM:
                                        if (i * size) < max_val:
                                            self.assertAlmostEqual(value, i*size)
                                    elif op == MPI.PROD:
                                        if (i ** size) < max_val:
                                            self.assertAlmostEqual(value, i**size)
                                    elif op == MPI.MAX:
                                        self.assertEqual(value, i)
                                    elif op == MPI.MIN:
                                        self.assertEqual(value, i)

    def testAllreduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                        buf = array(typecode, range(size))
                        sbuf = MPI.IN_PLACE
                        rbuf = mkbuf(buf, datatype)
                        try:
                            self.COMM.Allreduce(sbuf, rbuf, op)
                        except NotImplementedError:
                            return
                        max_val = maxvalue(buf)
                        for i, value in enumerate(buf):
                            if op == MPI.SUM:
                                if (i * size) < max_val:
                                    self.assertAlmostEqual(value, i*size)
                            elif op == MPI.PROD:
                                if (i ** size) < max_val:
                                    self.assertAlmostEqual(value, i**size)
                            elif op == MPI.MAX:
                                self.assertEqual(value, i)
                            elif op == MPI.MIN:
                                self.assertEqual(value, i)


class TestCollBufSelf(TestCollBufBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCollBufWorld(TestCollBufBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCollBufInplaceSelf(TestCollBufInplaceBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCollBufInplaceWorld(TestCollBufInplaceBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

if MPI.IN_PLACE is None:
    del TestCollBufInplaceBase
    del TestCollBufInplaceSelf
    del TestCollBufInplaceWorld

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
