#!/bin/env python

from mpi4py import MPI

child = MPI.COMM_WORLD.Spawn('child.py', [], MPI.COMM_WORLD.size+1, MPI.INFO_NULL, root=0)

print 'parent size: %d, child size: %d' %(child.size, child.remote_size)

if child.rank == 0:
    child.Send('ack', 0)

child.Disconnect()
