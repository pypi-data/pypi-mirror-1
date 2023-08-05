from mpi4py import MPI

pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# list of values in each process
data = [MPI.rank*100, MPI.rank**2]


# print input data
msg = "[%d] input:  %s" % (MPI.rank, data)
pprint(msg)


# allgather
data = MPI.WORLD.Allgather(data)


# print result data
msg = "[%d] result: %s" % (MPI.rank, data)
pprint(msg)
