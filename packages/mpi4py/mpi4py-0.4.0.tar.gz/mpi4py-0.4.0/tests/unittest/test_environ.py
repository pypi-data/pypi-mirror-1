import unittest
from mpi4py import MPI

class TestEnviron(unittest.TestCase):

    def testIsInitFini(self):
        self.assertTrue(MPI.Is_initialized())
        self.assertFalse(MPI.Is_finalized())

    def testThreadLevel(self):
        levels = [MPI.THREAD_SINGLE,
                  MPI.THREAD_FUNNELED,
                  MPI.THREAD_SERIALIZED,
                  MPI.THREAD_MULTIPLE]
        for i in xrange(len(levels)-1):
            if levels[i] is not None and \
                   levels[i+1] is not None:
                self.assertTrue(levels[i] < levels[i+1])
        try:
            provided = MPI.Query_thread()
            self.assertTrue(provided in levels)
        except NotImplementedError:
            pass
        try:
            flag = MPI.Is_thread_main()
            self.assertTrue(flag)
        except NotImplementedError:
            pass
            
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
        self.assertTrue(type(procname) is str)

    def testHostPorcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = range(size) + [MPI.PROC_NULL]
        self.assertTrue(MPI.HOST in vals)

    def testIOProcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = range(size) + [MPI.UNDEFINED,
                              MPI.ANY_SOURCE,
                              MPI.PROC_NULL]
        self.assertTrue(MPI.IO in vals)

       
if __name__ == '__main__':
    #unittest.main()
    try:
        unittest.main()
    except SystemExit:
        pass
