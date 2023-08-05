from mpi4py import MPI

rprint = MPI._rprint
pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

val = MPI.rank * 100 + MPI.rank % 2
tag = 1


# neighbors
prev = (MPI.size + MPI.rank - 1) % MPI.size
next = (MPI.rank + 1) % MPI.size


# initialize data list
data = 'I was born in process %d' % MPI.rank

rprint('')
rprint('Before:')
pprint("[%d] data: %s" % (MPI.rank,data))


# sendrecv
rprint('')
pprint("[%d] dest: %s -  source: %s" % (MPI.rank,next,prev))
data = MPI.WORLD.Sendrecv(data, dest = next, source = prev)


# show data
rprint('')
rprint('After:')
pprint("[%d] data: %s" % (MPI.rank,data))
