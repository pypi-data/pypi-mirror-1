from mpi4py import MPI

pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# data in all processes
data = []
for i in xrange(MPI.size):
    data += [ MPI.size * 10 + MPI.rank ]


# print input data
msg = "[%d] input:  %s" % (MPI.rank, data)
pprint(msg)


# alltoall
data = MPI.WORLD.Alltoall(data)


# print result data
msg = "[%d] result: %s" % (MPI.rank, data)
pprint(msg)
