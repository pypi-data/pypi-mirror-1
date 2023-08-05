from mpi4py import MPI

# data
buff = MPI.rank


# reduction operation
op   = MPI.SUM
MPI.rprint('op:   %s' % 'MPI.SUM')


# print input data
msg = "[%d] input:  %s" % (MPI.rank, buff)
MPI.pprint(msg)


# reduce
buff = MPI.WORLD.Allreduce(buff,op)


# print result data
msg = "[%d] result: %s" % (MPI.rank, buff)
MPI.pprint(msg)
