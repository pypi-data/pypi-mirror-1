import unittest
from mpi4py import MPI

class TestOp(unittest.TestCase):

    def testCreate(self):
        op = MPI.Op()
        #op.Init(0)
        #op.Free()

    def _test_call(self, op, args, res):
        self.assertEqual(op(*args), res)

    def testCall(self):
        self._test_call(MPI.MIN,  (2,3), 2)
        self._test_call(MPI.MAX,  (2,3), 3)
        self._test_call(MPI.SUM,  (2,3), 5)
        self._test_call(MPI.PROD, (2,3), 6)

    def testFree(self):
        self.assertRaises(MPI.Exception, MPI.OP_NULL.Free)
        for op in (MPI.MAX, MPI.MIN,
                   MPI.SUM, MPI.PROD,
                   MPI.LAND, MPI.BAND,
                   MPI.LOR, MPI.BOR,
                   MPI.LXOR, MPI.BXOR,
                   MPI.MAXLOC, MPI.MINLOC,
                   MPI.REPLACE,):
            self.assertRaises(MPI.Exception, op.Free)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
