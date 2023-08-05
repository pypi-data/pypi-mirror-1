from mpi4py import MPI

rprint = MPI._rprint
pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# root process
root = MPI.size/2
rprint('root: %d' % root, MPI.COMM_WORLD, root)


# data in all processes
data = [MPI.rank*10, MPI.rank**2]


# print input data
msg = "[%d] input:  %s" % (MPI.rank, data)
pprint(msg, MPI.COMM_WORLD, root)


# gather data from all to root
data = MPI.WORLD[root].Gather(data)


# print result data
msg = "[%d] result: %s" % (MPI.rank, data)
pprint(msg, MPI.COMM_WORLD, root)
