from mpi4py import MPI


# data in all processes
data = []
for i in xrange(MPI.size):
    data += [ MPI.size * 10 + MPI.rank ]


# print input data
msg = "[%d] input:  %s" % (MPI.rank, data)
MPI.pprint(msg)


# alltoall
data = MPI.WORLD.Alltoall(data)


# print result data
msg = "[%d] result: %s" % (MPI.rank, data)
MPI.pprint(msg)
