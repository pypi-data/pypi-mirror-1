from mpi4py import MPI

rprint = MPI._rprint
pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# data
buff = MPI.rank


# reduction operation
op   = MPI.SUM
rprint('op:   %s' % 'MPI.SUM')


# print input data
msg = "[%d] input:  %s" % (MPI.rank, buff)
pprint(msg)


# reduce
buff = MPI.WORLD.Allreduce(buff,op)


# print result data
msg = "[%d] result: %s" % (MPI.rank, buff)
pprint(msg)
