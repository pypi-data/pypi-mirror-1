from mpi4py import MPI

# root process
root = MPI.size/2
MPI.rprint('root: %d'%root, MPI.COMM_WORLD, root)


# data
buff = MPI.rank


# reduction operation
op   = MPI.SUM
MPI.rprint('op:   %s' % 'MPI.SUM', MPI.COMM_WORLD, root)


# print input data
msg = "[%d] input:  %s" % (MPI.rank, buff)
MPI.pprint(msg, MPI.COMM_WORLD, root)


# reduce
buff = MPI.WORLD.Reduce(buff,root,op)


# print result data
msg = "[%d] result: %s" % (MPI.rank, buff)
MPI.pprint(msg, MPI.COMM_WORLD, root)
