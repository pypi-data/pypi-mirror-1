from mpi4py import MPI

# list of values in each process
data = [MPI.rank*100, MPI.rank**2]


# print input data
msg = "[%d] input:  %s" % (MPI.rank, data)
MPI.pprint(msg)


# allgather
data = MPI.WORLD.Allgather(data)


# print result data
msg = "[%d] result: %s" % (MPI.rank, data)
MPI.pprint(msg)
