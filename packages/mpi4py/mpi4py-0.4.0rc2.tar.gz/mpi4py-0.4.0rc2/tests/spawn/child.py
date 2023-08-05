#!/bin/env python

from mpi4py import MPI

parent = MPI.Comm.Get_parent()

if parent.rank == 0:
    ack = parent.Recv('ack', 0)
    assert ack == 'ack'
    
parent.Disconnect()
