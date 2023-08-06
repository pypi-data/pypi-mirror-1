import sys, unittest
from mpi4py import MPI

# MPI.Comm.SERIALIZER = MPI.Pickle(protocol=0)
# MPI.Comm.SERIALIZER = MPI.Marshal

_basic = [None,
          True, False,
          -7, 0, 7, sys.maxint,
          -2.17, 0.0, 3.14,
          1+2j, 2-3j,
          'mpi4py',
          ]
messages = _basic
messages += [ list(_basic),
              tuple(_basic),
              dict([('k%d' % key, val)
                    for key, val in enumerate(_basic)])
              ]


class TestP2PObjBase(object):

    COMM = MPI.COMM_NULL

    def testSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.Send(smess,  MPI.PROC_NULL)
            rmess = self.COMM.Recv(None, MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.Send(smess,  rank+1, 0)
                rmess = smess
            elif rank == size - 1:
                rmess = self.COMM.Recv(None, rank-1, 0)
            else:
                rmess = self.COMM.Recv(None, rank-1, 0)
                self.COMM.Send(rmess,  rank+1, 0)
            self.assertEqual(rmess, smess)

    def testSendrecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            rmess = None
            rmess = self.COMM.Sendrecv(smess,  MPI.PROC_NULL, 0,
                                       None,   MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
            dest = (rank + 1) % size
            source = (rank - 1) % size
            rmess = self.COMM.Sendrecv(smess, dest,   0,
                                       None,  source, 0)
            self.assertEqual(rmess, smess)

    def testPingPong01(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.Send(smess,  MPI.PROC_NULL)
            rmess = self.COMM.Recv(None, MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.Send(smess,  rank+1, 0)
                rmess = self.COMM.Recv(None, rank+1, 0)
            elif rank == 1:
                rmess = self.COMM.Recv(None, rank-1, 0)
                self.COMM.Send(smess,  rank-1, 0)
            else:
                rmess = smess
            self.assertEqual(rmess, smess)


class TestP2PObjSelf(TestP2PObjBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PObjWorld(TestP2PObjBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestP2PObjSelfDup(TestP2PObjBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestP2PObjWorldDup(TestP2PObjBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
