import sys, unittest
from mpi4py import MPI
from mpi4py import _mpi

# MPI.Comm.SERIALIZER = MPI.Pickle(protocol=0)
# MPI.Comm.SERIALIZER = MPI.Pickle(protocol=-1)
# MPI.Comm.SERIALIZER = MPI.Marshal(0)
# MPI.Comm.SERIALIZER = MPI.Marshal(-1)

cumsum  = lambda seq: _mpi._reduce(lambda x, y: x+y, seq, 0)

cumprod = lambda seq: _mpi._reduce(lambda x, y: x*y, seq, 1)

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



[None, True, False, 7, 3.14, 1+2j, 'mpi4py',
            [None, 7, 3.14, 1+2j, 'mpi4py'],
            (None, 7, 3.14, 1+2j, 'mpi4py'),
            dict(k1=None,k2=7,k3=3.14,k4=1+2j,k5='mpi4py')]

#messages = [messages*1000, messages*1000]

class TestCollObjBase(object):

    COMM = MPI.COMM_NULL

    def testBarrier(self):
        self.COMM.Barrier()

    def testBcast(self):
        for smess in messages:
            for root in range(self.COMM.Get_size()):
                rmess = self.COMM.Bcast(smess, root=root)
                self.assertEqual(smess, rmess)

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            for root in range(size):
                rmess = self.COMM.Gather(smess, root=root)
                if rank == root:
                    self.assertEqual(rmess, [smess] * size)
                else:
                    self.assertEqual(rmess, None)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            for root in range(size):
                if rank == root:
                    rmess = self.COMM.Scatter([smess] * size, root=root)
                else:
                    rmess = self.COMM.Scatter(None, root=root)
                self.assertEqual(rmess, smess)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            rmess = self.COMM.Allgather(smess, None)
            self.assertEqual(rmess, [smess] * size)

    def testAlltoall(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            rmess = self.COMM.Alltoall([smess] * size, None)
            self.assertEqual(rmess, [smess] * size)

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for root in range(size):
            for op in (MPI.SUM, MPI.PROD,
                       MPI.MAX, MPI.MIN,
                       MPI.MAXLOC, MPI.MINLOC):
                value = self.COMM.Reduce(rank, None, op=op, root=root)
                if rank != root:
                    self.assertTrue(value is None)
                else:
                    if op == MPI.SUM:
                        self.assertEqual(value, cumsum(range(size)))
                    elif op == MPI.PROD:
                        self.assertEqual(value, cumprod(range(size)))
                    elif op == MPI.MAX:
                        self.assertEqual(value, size-1)
                    elif op == MPI.MIN:
                        self.assertEqual(value, 0)
                    elif op == MPI.MAXLOC:
                        self.assertEqual(value[1], size-1)
                    elif op == MPI.MINLOC:
                        self.assertEqual(value[1], 0)

    def testAllreduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for op in (MPI.SUM, MPI.PROD,
                       MPI.MAX, MPI.MIN,
                       MPI.MAXLOC, MPI.MINLOC):
            value = self.COMM.Allreduce(rank, None, op)
            if op == MPI.SUM:
                self.assertEqual(value, cumsum(range(size)))
            elif op == MPI.PROD:
                self.assertEqual(value, cumprod(range(size)))
            elif op == MPI.MAX:
                self.assertEqual(value, size-1)
            elif op == MPI.MIN:
                self.assertEqual(value, 0)
            elif op == MPI.MAXLOC:
                self.assertEqual(value[1], size-1)
            elif op == MPI.MINLOC:
                self.assertEqual(value[1], 0)


    def testScan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        # --
        sscan = self.COMM.Scan(size, op=MPI.SUM)
        self.assertEqual(sscan, cumsum([size]*(rank+1)))
        # --
        rscan = self.COMM.Scan(rank, op=MPI.SUM)
        self.assertEqual(rscan, cumsum(range(rank+1)))
        # --
        minloc = self.COMM.Scan(rank, op=MPI.MINLOC)
        maxloc = self.COMM.Scan(rank, op=MPI.MAXLOC)
        self.assertEqual(minloc, (0, 0))
        self.assertEqual(maxloc, (rank, rank))

    def testExscan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        # --
        try:
            sscan = self.COMM.Exscan(size, op=MPI.SUM)
        except NotImplementedError:
            return
        if rank == 0:
            self.assertTrue(sscan is None)
        else:
            self.assertEqual(sscan, cumsum([size]*(rank)))
        # --
        rscan = self.COMM.Exscan(rank, op=MPI.SUM)
        if rank == 0:
            self.assertTrue(rscan is None)
        else:
            self.assertEqual(rscan, cumsum(range(rank)))
        #
        minloc = self.COMM.Exscan(rank, op=MPI.MINLOC)
        maxloc = self.COMM.Exscan(rank, op=MPI.MAXLOC)
        if rank == 0:
            self.assertEqual(minloc, None)
            self.assertEqual(maxloc, None)
        else:
            self.assertEqual(minloc, (0, 0))
            self.assertEqual(maxloc, (rank-1, rank-1))

class TestInterCollObjBase(object):

    BASECOMM = MPI.COMM_NULL

    def setUp(self):
        self.INTRACOMM = MPI.COMM_NULL
        self.INTERCOMM = MPI.COMM_NULL
        if self.BASECOMM == MPI.COMM_NULL: return
        BASE_SIZE = self.BASECOMM.Get_size()
        BASE_RANK = self.BASECOMM.Get_rank()
        if BASE_SIZE < 2:
            return
        if BASE_RANK < BASE_SIZE // 2 :
            self.COLOR = 0
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = BASE_SIZE // 2
        else:
            self.COLOR = 1
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = 0
        self.INTRACOMM = self.BASECOMM.Split(self.COLOR, key=0)
        self.INTERCOMM = self.INTRACOMM.Create_intercomm(self.LOCAL_LEADER,
                                                         self.BASECOMM,
                                                         self.REMOTE_LEADER)

    def tearDown(self):
        if self.INTRACOMM != MPI.COMM_NULL:
            self.INTRACOMM.Free()
        if self.INTERCOMM != MPI.COMM_NULL:
            self.INTERCOMM.Free()

    def testBarrier(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        try:
            self.INTERCOMM.Barrier()
        except NotImplementedError:
            return

    def testBcast(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            for color in [0, 1]:
                try:
                    if self.COLOR == color:
                        for root in range(size):
                            if root == rank:
                                rmess = self.INTERCOMM.Bcast(smess, root=MPI.ROOT)
                            else:
                                rmess = self.INTERCOMM.Bcast(None, root=MPI.PROC_NULL)
                            self.assertEqual(rmess, None)
                    else:
                        for root in range(rsize):
                            rmess = self.INTERCOMM.Bcast(None, root=root)
                            self.assertEqual(rmess, smess)
                except NotImplementedError:
                    return

    def testGather(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            for color in [0, 1]:
                try:
                    if self.COLOR == color:
                        for root in range(size):
                            if root == rank:
                                rmess = self.INTERCOMM.Gather(smess, root=MPI.ROOT)
                                self.assertEqual(rmess, [smess] * rsize)
                            else:
                                rmess = self.INTERCOMM.Gather(None, root=MPI.PROC_NULL)
                                self.assertEqual(rmess, None)
                    else:
                        for root in range(rsize):
                            rmess = self.INTERCOMM.Gather(smess, root=root)
                            self.assertEqual(rmess, None)
                except NotImplementedError:
                    return

    def testScatter(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            for color in [0, 1]:
                try:
                    if self.COLOR == color:
                        for root in range(size):
                            if root == rank:
                                rmess = self.INTERCOMM.Scatter([smess] * rsize, root=MPI.ROOT)
                            else:
                                rmess = self.INTERCOMM.Scatter(None, root=MPI.PROC_NULL)
                            self.assertEqual(rmess, None)
                    else:
                        for root in range(rsize):
                            rmess = self.INTERCOMM.Scatter(None, root=root)
                            self.assertEqual(rmess, smess)
                except NotImplementedError:
                    return

    def testAllgather(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            try:
                rmess = self.INTERCOMM.Allgather(smess)
                #rmess = [smess] * rsize
            except NotImplementedError:
                return
            self.assertEqual(rmess, [smess] * rsize)

    def testAlltoall(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            try:
                rmess = self.INTERCOMM.Alltoall([smess] * rsize)
            except NotImplementedError:
                return
            self.assertEqual(rmess, [smess] * rsize)

    def testReduce(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
            for color in [0, 1]:
                try:
                    if self.COLOR == color:
                        for root in range(size):
                            if root == rank:
                                value = self.INTERCOMM.Reduce(None, op=op, root=MPI.ROOT)
                                if op == MPI.SUM:
                                    self.assertEqual(value, cumsum(range(rsize)))
                                elif op == MPI.PROD:
                                    self.assertEqual(value, cumprod(range(rsize)))
                                elif op == MPI.MAX:
                                    self.assertEqual(value, rsize-1)
                                elif op == MPI.MIN:
                                    self.assertEqual(value, 0)
                            else:
                                value = self.INTERCOMM.Reduce(None, op=op, root=MPI.PROC_NULL)
                                self.assertEqual(value, None)
                    else:
                        for root in range(rsize):
                            value = self.INTERCOMM.Reduce(rank, op=op, root=root)
                            self.assertEqual(value, None)
                except NotImplementedError:
                    return

    def testAllreduce(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
            try:
                value = self.INTERCOMM.Allreduce(rank, None, op)
            except NotImplementedError:
                return
            if op == MPI.SUM:
                self.assertEqual(value, cumsum(range(rsize)))
            elif op == MPI.PROD:
                self.assertEqual(value, cumprod(range(rsize)))
            elif op == MPI.MAX:
                self.assertEqual(value, rsize-1)
            elif op == MPI.MIN:
                self.assertEqual(value, 0)


class TestCollObjSelf(TestCollObjBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCollObjWorld(TestCollObjBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCollObjSelfDup(TestCollObjBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCollObjWorldDup(TestCollObjBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestInterCollObjWorld(TestInterCollObjBase, unittest.TestCase):
    BASECOMM = MPI.COMM_WORLD

class TestInterCollObjWorldDup(TestInterCollObjBase, unittest.TestCase):
    BASECOMM = MPI.COMM_NULL
    def setUp(self):
        self.BASECOMM = MPI.COMM_WORLD.Dup()
        super(TestInterCollObjWorldDup, self).setUp()
    def tearDown(self):
        self.BASECOMM.Free()
        super(TestInterCollObjWorldDup, self).tearDown()

_name, _version = MPI._mpi_info()
if _name == 'OpenMPI':
    if _version < (1, 2, 4):
        del TestInterCollObjWorld
        del TestInterCollObjWorldDup

if MPI.ROOT is None:
    del TestInterCollObjBase
    del TestInterCollObjWorld
    del TestInterCollObjWorldDup

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
