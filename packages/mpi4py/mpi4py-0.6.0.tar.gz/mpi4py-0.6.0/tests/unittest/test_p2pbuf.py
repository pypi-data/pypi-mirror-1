import unittest
from mpi4py import MPI
from array import array

typemap = dict(#b=MPI.CHAR,
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


class TestP2PBufBase(object):

    COMM = MPI.COMM_NULL

    def testSendrecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for s in range(0, size):
                        sbuf = array(typecode, [s] * s)
                        rbuf = array(typecode, [-1] * s)
                        self.COMM.Sendrecv(mkbuf(sbuf, datatype), dest, 0,
                                           mkbuf(rbuf, datatype), source, 0)
                        for value in rbuf:
                            self.assertEqual(value, s)

    def testSendRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for s in range(0, size):
                        sbuf = array(typecode, [s] * s)
                        rbuf = array(typecode, [-1] * s)
                        mem  = array(typecode, [0] * (s+MPI.BSEND_OVERHEAD))
                        if size == 1:
                            MPI.Attach_buffer(mem)
                            rbuf = sbuf
                            MPI.Detach_buffer()
                        elif rank == 0:
                            MPI.Attach_buffer(mem)
                            self.COMM.Bsend(mkbuf(sbuf, datatype), 1, 0)
                            MPI.Detach_buffer()
                            self.COMM.Send(mkbuf(sbuf, datatype), 1, 0)
                            self.COMM.Ssend(mkbuf(sbuf, datatype), 1, 0)
                            self.COMM.Recv(mkbuf(rbuf, datatype),  1, 0)
                            self.COMM.Recv(mkbuf(rbuf, datatype), 1, 0)
                            self.COMM.Recv(mkbuf(rbuf, datatype), 1, 0)
                        elif rank == 1:
                            self.COMM.Recv(mkbuf(rbuf, datatype), 0, 0)
                            self.COMM.Recv(mkbuf(rbuf, datatype), 0, 0)
                            self.COMM.Recv(mkbuf(rbuf, datatype), 0, 0)
                            MPI.Attach_buffer(mem)
                            self.COMM.Bsend(mkbuf(sbuf, datatype), 0, 0)
                            MPI.Detach_buffer()
                            self.COMM.Send(mkbuf(sbuf, datatype), 0, 0)
                            self.COMM.Ssend(mkbuf(sbuf, datatype), 0, 0)
                        else:
                            rbuf = sbuf

                        for value in rbuf:
                            self.assertEqual(value, s)


    def testPersistent(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for s in range(size):
                        #
                        sbuf = array(typecode, [s]*s)
                        rbuf = array(typecode, [-1]*s)
                        sendreq = self.COMM.Send_init(mkbuf(sbuf, datatype), dest, 0)
                        recvreq = self.COMM.Recv_init(mkbuf(rbuf, datatype), source, 0)
                        sendreq.Start()
                        recvreq.Start()
                        sendreq.Wait()
                        recvreq.Wait()
                        self.assertNotEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertNotEqual(recvreq, MPI.REQUEST_NULL)
                        sendreq.Free()
                        recvreq.Free()
                        #
                        sbuf = array(typecode, [s]*s)
                        rbuf = array(typecode, [-1]*s)
                        sendreq = self.COMM.Send_init(mkbuf(sbuf, datatype), dest, 0)
                        recvreq = self.COMM.Recv_init(mkbuf(rbuf, datatype), source, 0)
                        reqlist = [sendreq, recvreq]
                        MPI.Prequest.Startall(reqlist)
                        index = MPI.Prequest.Waitany(reqlist)
                        self.assertTrue(index in [0, 1])
                        self.assertNotEqual(reqlist[index], MPI.REQUEST_NULL)
                        MPI.Prequest.Waitall(reqlist)
                        for preq in reqlist:
                            self.assertNotEqual(preq, MPI.REQUEST_NULL)
                            preq.Free()
                            self.assertEqual(preq, MPI.REQUEST_NULL)
                        for value in rbuf:
                            self.assertEqual(value, s)


class TestP2PBufSelf(TestP2PBufBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PBufWorld(TestP2PBufBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD



if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
