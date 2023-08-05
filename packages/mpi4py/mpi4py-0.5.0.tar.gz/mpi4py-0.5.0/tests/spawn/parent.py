#! /usr/bin/env python

from mpi4py import MPI
import sys

child = MPI.COMM_WORLD.Spawn(sys.executable, ['child.py'],
                             MPI.COMM_WORLD.size+1, MPI.INFO_NULL, root=0)
assert child != MPI.COMM_NULL

print 'parent size: %d, child size: %d' %(child.size, child.remote_size)

if child.rank == 0:
    child.Send('ack', 0)

child.Disconnect()
assert child == MPI.COMM_NULL
