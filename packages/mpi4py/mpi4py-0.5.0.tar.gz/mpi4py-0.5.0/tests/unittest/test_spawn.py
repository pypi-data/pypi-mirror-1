import unittest, sys
from mpi4py import MPI

class TestSpawnBase(object):

    COMM = MPI.COMM_NULL
    COMMAND = sys.executable
    ARGS = ['-c', ';'.join([
        'from mpi4py import MPI',
        'parent = MPI.Comm.Get_parent()',
        'parent.Disconnect()',
        ])]

    MAXPROCS = 1
    INFO = MPI.INFO_NULL
    ROOT = 0
    
    def testCommSpawn(self):
        child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                info=self.INFO, root=self.ROOT)
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, self.MAXPROCS)
        child.Disconnect()

    def testReturnedErrcodes(self):
        errcodes = []
        child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                info=self.INFO, root=self.ROOT,
                                errcodes=errcodes)
        rank = self.COMM.Get_rank()
        if rank == self.ROOT:
            self.assertEqual(len(errcodes), self.MAXPROCS)
            for errcode in errcodes:
                self.assertEqual(errcode, MPI.SUCCESS)
        else:
            self.assertEqual(errcodes, [])
        child.Disconnect()

    def testArgsOnlyAtRoot(self):
        rank = self.COMM.Get_rank()
        if rank == self.ROOT:
            child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                    info=self.INFO, root=self.ROOT)
        else:
            child = self.COMM.Spawn(None, None, MPI.UNDEFINED,
                                    info=None, root=self.ROOT)
        child.Disconnect()

class TestSpawnSelf(TestSpawnBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestSpawnWorld(TestSpawnBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestSpawnWorldMany(TestSpawnBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD
    MAXPROCS = MPI.COMM_WORLD.Get_size()


_SKIP_TEST = False

if MPI.Get_version() < (2,0):
    _SKIP_TEST = True
_name, _version = MPI._mpi_info()
if _name == 'OpenMPI':
    if MPI.Query_thread() > MPI.THREAD_SINGLE:
        _SKIP_TEST = True
if _name == 'MPICH2':
    if MPI.APPNUM == MPI.UNDEFINED:
        _SKIP_TEST = True

if _SKIP_TEST:
    del TestSpawnBase
    del TestSpawnSelf
    del TestSpawnWorld
    del TestSpawnWorldMany

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
