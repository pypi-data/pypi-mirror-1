## mpiexec -n 2 python ex-2.03.py

# Process 0 sends a message to process 1

# --------------------------------------------------------------------

import mpi4py.MPI as MPI

if MPI.WORLD_SIZE < 2 : raise SystemExit

# --------------------------------------------------------------------

tag = 99
status = MPI.Status()

myrank = MPI.COMM_WORLD.Get_rank()

if myrank == 0:
    msg = "Hello there"
    MPI.COMM_WORLD.Send(msg, 1, tag)
elif myrank == 1:
    msg = MPI.COMM_WORLD.Recv(None, 0, tag, status)

# --------------------------------------------------------------------

if myrank == 1:
    assert msg == "Hello there"
    assert status.source == 0
    assert status.tag == tag
    assert status.error == MPI.SUCCESS
