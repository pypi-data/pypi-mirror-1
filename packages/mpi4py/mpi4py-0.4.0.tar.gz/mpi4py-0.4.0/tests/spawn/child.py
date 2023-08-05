#! /usr/bin/env python

from mpi4py import MPI

parent = MPI.Comm.Get_parent()
assert parent != MPI.COMM_NULL

if parent.rank == 0:
    ack = parent.Recv(None, 0)
    assert ack == 'ack'

parent.Disconnect()
assert parent == MPI.COMM_NULL
