import unittest
from mpi4py import MPI

class TestEnviron(unittest.TestCase):

    def testIsInitFini(self):
        self.assertTrue(MPI.Is_initialized())
        self.assertFalse(MPI.Is_finalized())

    def testVersion(self):
        version = MPI.Get_version()
        self.assertEqual(len(version), 2)
        self.assertTrue(type(version[0]) is int)
        self.assertTrue(type(version[1]) is int)

    def testTime(self):
        tick = MPI.Wtick()
        self.assertTrue(tick > 0.0)
        time1 = MPI.Wtime()
        time2 = MPI.Wtime()
        self.assertTrue(time1 <= time2)

    def testProcessorName(self):
        procname = MPI.Get_processor_name()
        self.assertTrue(isinstance(procname, type('')))

    def testHostPorcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = list(range(size)) + [MPI.PROC_NULL]
        self.assertTrue(MPI.HOST in vals)

    def testIOProcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = list(range(size)) + [MPI.UNDEFINED,
                                    MPI.ANY_SOURCE,
                                    MPI.PROC_NULL]
        self.assertTrue(MPI.IO in vals)

    def testAppNum(self):
        appnum = MPI.APPNUM
        self.assertTrue(appnum == MPI.UNDEFINED or appnum >= 0)

    def testUniverseSize(self):
        univsz = MPI.UNIVERSE_SIZE
        self.assertTrue(univsz == MPI.UNDEFINED or univsz >= 0)




if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
