from mpi4py import MPI

rprint = MPI._rprint
pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# root process
root = MPI.size/2
rprint('root: %d'%root, MPI.COMM_WORLD, root)


# some data in root,
# no data in others
if MPI.rank == root:
    data = [ MPI.size*10+i for i in xrange(MPI.size) ]
else:
    data = None


# print input data
msg = "[%d] input:  %s" % (MPI.rank, data)
pprint(msg, MPI.COMM_WORLD, root)


# scatter data from root to all
# two calling forms
if 1:
    data = MPI.WORLD[root].Scatter(data)
else:
    if MPI.rank == root: data = MPI.WORLD[root].Scatter(data)
    else:                data = MPI.WORLD[root].Scatter()


# print result data
msg = "[%d] result: %s" % (MPI.rank, data)
pprint(msg, MPI.COMM_WORLD, root)
