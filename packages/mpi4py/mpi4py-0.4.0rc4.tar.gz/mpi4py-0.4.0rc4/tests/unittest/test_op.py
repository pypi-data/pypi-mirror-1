import unittest
from mpi4py import MPI

class TestOp(unittest.TestCase):

    def testCreate(self):
        op = MPI.Op()
        #op.Init(0)
        #op.Free()

    def testCall(self):
        res = MPI.SUM(2,3)
        self.assertEqual(res, 5)
        
if __name__ == '__main__':
    #unittest.main()
    try:
        unittest.main()
    except SystemExit:
        pass
