# Jacobi computation, using persitent requests

import mpi4py.MPI as MPI
import numpy


n = 5 * MPI.WORLD_SIZE

# compute number of processes and myrank
p = MPI.COMM_WORLD.Get_size()
myrank = MPI.COMM_WORLD.Get_rank()

# compute size of local block
m = n/p
if myrank < (n - p * m):
    m = m + 1

#compute neighbors
if myrank == 0:
    left = MPI.PROC_NULL
else:
    left = myrank - 1
if myrank == p - 1:
    right = MPI.PROC_NULL
else:
    right = myrank + 1

# allocate local arrays
A = numpy.empty((n+2, m+2), dtype=float, order='fortran')
B = numpy.empty((n, m), dtype=float, order='fortran')

A.fill(1)
A[0, :] = A[-1, :] = 0
A[:, 0] = A[:, -1] = 0

# create persintent requests
tag = 0
sreq1 = MPI.COMM_WORLD.Send_init((B[:,  0], MPI.DOUBLE), left,  tag)
sreq2 = MPI.COMM_WORLD.Send_init((B[:, -1], MPI.DOUBLE), right, tag)
rreq1 = MPI.COMM_WORLD.Recv_init((A[:,  0], MPI.DOUBLE), left,  tag)
rreq2 = MPI.COMM_WORLD.Recv_init((A[:, -1], MPI.DOUBLE), right, tag)
reqlist = [sreq1, sreq2, rreq1, rreq2]

for req in reqlist:
    assert req != MPI.REQUEST_NULL

# main loop
converged = False
while not converged:
    # compute boundary columns
    N, S = A[ :-2, 1], A[2:,   1]
    E, W = A[1:-1, 0], A[1:-1, 2]
    C = B[:, 0]
    numpy.add(N, S, C)
    numpy.add(C, E, C)
    numpy.add(C, W, C)
    C *= 0.25
    N, S = A[ :-2, -2], A[2:,   -2]
    E, W = A[1:-1, -3], A[1:-1, -1]
    C = B[:, -1]
    numpy.add(N, S, C)
    numpy.add(C, E, C)
    numpy.add(C, W, C)
    C *= 0.25
    # start communication
    #MPI.Prequest.Startall(reqlist)
    for r in reqlist:
        r.Start()
    # compute interior
    N, S = A[ :-2, 2:-2], A[2,    2:-2]
    E, W = A[1:-1, 2:-2], A[1:-1, 2:-2]
    C = B[:, 1:-1]
    numpy.add(N, S, C)
    numpy.add(E, C, C)
    numpy.add(W, C, C)
    C *= 0.25
    A[1:-1, 1:-1] = B
    # complete communication
    #MPI.Prequest.Waitall(reqlist)
    break
    for r in reqlist:
        r.Wait()
        print type(r), hex(r), hex(MPI.REQUEST_NULL)
        #assert r
    #break
    # convergence
    myconv = numpy.allclose(B, 0)
    converged = MPI.COMM_WORLD.Allreduce(myconv, op=MPI.LAND)
    
# free persintent requests
## for req in reqlist:
##     req.Free()
