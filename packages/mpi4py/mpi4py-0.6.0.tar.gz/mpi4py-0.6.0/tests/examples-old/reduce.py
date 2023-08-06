from mpi4py import MPI

rprint = MPI._rprint
pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# root process
root = MPI.size/2
rprint('root: %d'%root, MPI.COMM_WORLD, root)


# data
buff = MPI.rank


# reduction operation
op   = MPI.SUM
rprint('op:   %s' % 'MPI.SUM', MPI.COMM_WORLD, root)


# print input data
msg = "[%d] input:  %s" % (MPI.rank, buff)
pprint(msg, MPI.COMM_WORLD, root)


# reduce
buff = MPI.WORLD.Reduce(buff,root,op)


# print result data
msg = "[%d] result: %s" % (MPI.rank, buff)
pprint(msg, MPI.COMM_WORLD, root)
