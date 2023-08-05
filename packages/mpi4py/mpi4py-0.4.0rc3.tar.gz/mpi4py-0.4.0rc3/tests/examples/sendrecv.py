from mpi4py import MPI


val = MPI.rank * 100 + MPI.rank % 2
tag = 1


# neighbors
prev = (MPI.size + MPI.rank - 1) % MPI.size
next = (MPI.rank + 1) % MPI.size


# initialize data list
data = 'I was born in process %d' % MPI.rank

MPI.rprint('')
MPI.rprint('Before:')
MPI.pprint("[%d] data: %s" % (MPI.rank,data))


# sendrecv
MPI.rprint('')
MPI.pprint("[%d] dest: %s -  source: %s" % (MPI.rank,next,prev))
data = MPI.WORLD.Sendrecv(data, dest = next, source = prev)


# show data
MPI.rprint('')
MPI.rprint('After:')
MPI.pprint("[%d] data: %s" % (MPI.rank,data))
