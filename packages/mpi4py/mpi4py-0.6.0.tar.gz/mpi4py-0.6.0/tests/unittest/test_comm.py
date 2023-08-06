import sys, unittest
from mpi4py import MPI

class TestCommBase(object):

    def testProperties(self):
        comm = self.COMM
        self.assertEqual(comm.Get_size(), comm.size)
        self.assertEqual(comm.Get_rank(), comm.rank)
        self.assertEqual(comm.Is_intra(), comm.is_intra)
        self.assertEqual(comm.Is_inter(), comm.is_inter)
        self.assertEqual(comm.Get_topology(), comm.topology)

    def testGroup(self):
        comm  = self.COMM
        group = self.COMM.Get_group()
        self.assertEqual(comm.Get_size(), group.Get_size())
        self.assertEqual(comm.Get_rank(), group.Get_rank())
        group.Free()
        self.assertEqual(group, MPI.GROUP_NULL)

    def testContructor(self):
        comm = MPI.Comm(self.COMM)
        self.assertEqual(comm, self.COMM)
        self.assertNotEqual(comm, MPI.COMM_NULL)

    def testCloneFree(self):
        comm = self.COMM.Clone()
        comm.Free()
        self.assertEqual(comm, MPI.COMM_NULL)

    def testCompare(self):
        results = (MPI.IDENT, MPI.CONGRUENT, MPI.SIMILAR, MPI.UNEQUAL)
        ccmp = MPI.Comm.Compare(self.COMM, MPI.COMM_WORLD)
        self.assertTrue(ccmp in results)
        ccmp = MPI.Comm.Compare(self.COMM, self.COMM)
        self.assertEqual(ccmp, MPI.IDENT)
        comm = self.COMM.Dup()
        ccmp = MPI.Comm.Compare(self.COMM, comm)
        comm.Free()
        self.assertEqual(ccmp, MPI.CONGRUENT)
        cmp_null = lambda: MPI.Comm.Compare(self.COMM, MPI.COMM_NULL)
        self.assertRaises(MPI.Exception, cmp_null)

    def testBarrier(self):
        self.COMM.Barrier()

    def testBcast(self):
        messages = [ None, 7, 3.14, 1+2j, 'mpi4py',
                    [None, 7, 3.14, 1+2j, 'mpi4py'],
                    (None, 7, 3.14, 1+2j, 'mpi4py'),
                     dict(k1=None,k2=7,k3=3.14,k4=1+2j,k5='mpi4py')]
        for smess in messages:
            rmess = self.COMM.Bcast(smess)
            self.assertEqual(smess, rmess)
            for root in range(self.COMM.Get_size()):
                rmess = self.COMM.Bcast(smess, root)
                self.assertEqual(smess, rmess)

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for root in range(size):
            rmess = self.COMM.Gather(rank, None, root)
            if rank == root:
                self.assertEqual(rmess, list(range(size)))
            else:
                self.assertEqual(rmess, None)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for root in range(size):
            smess = [rank + root] * size
            rmess = self.COMM.Scatter(smess, None, root)
            self.assertEqual(rmess, root * 2)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        rmess = self.COMM.Allgather(rank, None)
        self.assertEqual(rmess, list(range(size)))

    def testAlltoall(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        smess = [rank] * size
        rmess = self.COMM.Alltoall(smess, None)
        self.assertEqual(rmess, list(range(size)))

    def testGetSetName(self):
        try:
            name = self.COMM.Get_name()
            self.COMM.Set_name('comm')
            self.assertEqual(self.COMM.Get_name(), 'comm')
            self.COMM.Set_name(name)
            self.assertEqual(self.COMM.Get_name(), name)
        except NotImplementedError:
            pass

    def testGetParent(self):
        try:
            parent = MPI.Comm.Get_parent()
            if parent == MPI.COMM_NULL:
                self.assertRaises(MPI.Exception, parent.Disconnect)
        except NotImplementedError:
            pass


class TestCommNull(unittest.TestCase):

    def testNull(self):
        COMM_NULL = MPI.COMM_NULL
        comm_null = MPI.Comm(COMM_NULL)
        self.assertEqual(comm_null, COMM_NULL)
        cmpnull = lambda: MPI.Comm.Compare(COMM_NULL, COMM_NULL)
        self.assertRaises(MPI.Exception, cmpnull)
        for meth in ('Get_size', 'Get_rank', 'Is_inter', 'Is_intra',
                     'Get_group', 'Get_topology', 'Get_errhandler',
                     'Clone', 'Free', 'Abort'):
            bound_method = getattr(COMM_NULL, meth)
            self.assertRaises(MPI.Exception, bound_method)
            try:
                bound_method()
                raise AssertionError
            except MPI.Exception:
                exc = sys.exc_info()[1]
                self.assertEqual(exc.Get_error_class(), MPI.ERR_COMM)

    def testInterNull(self):
        comm_null = MPI.Intercomm(MPI.COMM_NULL)
        self.assertRaises(MPI.Exception, comm_null.Get_remote_group)
        self.assertRaises(MPI.Exception, comm_null.Get_remote_size)
        comm_null_Dup    = lambda : comm_null.Dup()
        comm_null_Create = lambda : comm_null.Create(group=MPI.GROUP_EMPTY)
        comm_null_Split  = lambda : comm_null.Split(color=0,key=0)
        comm_null_Merge  = lambda : comm_null.Merge(high=True)
        self.assertRaises(MPI.Exception, comm_null_Dup)
        self.assertRaises(MPI.Exception, comm_null_Create)
        self.assertRaises(MPI.Exception, comm_null_Split)
        self.assertRaises(MPI.Exception, comm_null_Merge)


class TestCommSelf(TestCommBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF
    def testSize(self):
        size = self.COMM.Get_size()
        self.assertEqual(size, 1)
    def testRank(self):
        rank = self.COMM.Get_rank()
        self.assertEqual(rank, 0)
    def testFree(self):
        self.assertRaises(MPI.Exception, MPI.COMM_SELF.Free)
        self.assertRaises(MPI.Exception, MPI.__COMM_SELF__.Free)


class TestCommWorld(TestCommBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD
    def testSize(self):
        size = self.COMM.Get_size()
        self.assertTrue(size >= 1)
    def testRank(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        self.assertTrue(rank >= 0 and rank < size)
    def testFree(self):
        self.assertRaises(MPI.Exception, MPI.COMM_WORLD.Free)
        self.assertRaises(MPI.Exception, MPI.__COMM_WORLD__.Free)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
