import unittest, sys
from mpi4py import MPI

class TestSpawn(unittest.TestCase):

    def testSpawn(self):
        python = sys.executable
        cmd    = ['from mpi4py import MPI',
                  'parent = MPI.Comm.Get_parent()',
                  'parent.Disconnect()',
                  ]
        args = ['-c', ';'.join(cmd)]
        child = MPI.COMM_WORLD.Spawn(python, args,
                                     maxprocs=1, info=MPI.INFO_NULL, root=0)
        child.Disconnect()
       
if __name__ == '__main__':
    #unittest.main()
    try:
        unittest.main()
    except SystemExit:
        pass
