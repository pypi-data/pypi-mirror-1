from mpi4py import MPI

pprint = lambda msg, root: MPI._pprint(msg, MPI.COMM_WORLD, root)
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# root process
root = MPI.size/2
if MPI.rank == root: print 'root: %d' % root


# some data in root,
# no data in others
if MPI.rank == root:
    import math
    data = [math.pi, 'dalcinl', {'K': 0,'M': 1}]
    del math
else:
    data = None


# print input data
msg = "[%d] input:  %s" % (MPI.rank, data)
pprint(msg,root)

# broadcast data from root to others
# two calling forms
if 1:
    data = MPI.WORLD[root].Bcast(data)
else:
    if MPI.rank == root: data = MPI.WORLD[root].Bcast(data)
    else:                data = MPI.WORLD[root].Bcast()
    

# print result data
msg = "[%d] result: %s" % (MPI.rank, data)
pprint(msg,root)
