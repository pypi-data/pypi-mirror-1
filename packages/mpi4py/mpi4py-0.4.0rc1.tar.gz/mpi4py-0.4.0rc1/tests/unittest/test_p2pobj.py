import unittest
from mpi4py import MPI

# MPI.Comm.SERIALIZER = MPI.Pickle(protocol=0)
# MPI.Comm.SERIALIZER = MPI.Marshal

messages = [None, 7, 3.14, 1+2j, 'mpi4py',
            [None, 7, 3.14, 1+2j, 'mpi4py'],
            (None, 7, 3.14, 1+2j, 'mpi4py'),
            dict(k1=None,k2=7,k3=3.14,k4=1+2j,k5='mpi4py')]

class TestP2PObjBase(object):
    
    COMM = MPI.COMM_NULL

    def testSendrecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            rmess = None
            rmess = self.COMM.Sendrecv(smess,  MPI.PROC_NULL, 0,
                                       None,   MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
                               
            #rmess = self.COMM.Sendrecv(smess, rank, 0,
            #                           None,  rank, 0)
            #self.assertEqual(rmess, smess)

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
    #unittest.main()
    try:
        unittest.main()
    except SystemExit:
        pass
    
