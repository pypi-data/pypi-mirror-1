## mpiexec -n 2 python ex-2.01.py

# Process 0 sends a message to process 1

# --------------------------------------------------------------------

import numpy
import mpi4py.MPI as MPI

if MPI.WORLD_SIZE < 2 : raise SystemExit

# --------------------------------------------------------------------

s = "Hello there"

msg = numpy.zeros(20, dtype='c')
tag = 99
status = MPI.Status()

myrank = MPI.COMM_WORLD.Get_rank()

if myrank == 0:
    msg[:len(s)] = s
    MPI.COMM_WORLD.Send([msg, len(s)+1, MPI.CHAR], 1, tag)
elif myrank == 1:
    MPI.COMM_WORLD.Recv([msg, 20, MPI.CHAR], 0, tag, status)

# --------------------------------------------------------------------

if myrank == 1:
    assert list(msg[:len(s)]) == list(s)
    assert status.source == 0
    assert status.tag == tag
    assert status.error == MPI.SUCCESS
    assert status.Get_count(MPI.CHAR) == len(s)+1

# --------------------------------------------------------------------
