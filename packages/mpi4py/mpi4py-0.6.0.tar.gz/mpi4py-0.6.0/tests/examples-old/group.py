from mpi4py import MPI

MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

# get group of COMM_WORLD
group = MPI.WORLD.Get_group()

# part group in halves
halve  = range(0, MPI.size/2)
group1 = group.Incl(halve)
group2 = group.Excl(halve)

# range of ranks for each group
ranks1 = range(group1.Get_size())
ranks2 = range(group2.Get_size())

# map group ranks to COMM_WORLD rank
tr1 = MPI.Group.Translate_ranks(group1, ranks1, group)
tr2 = MPI.Group.Translate_ranks(group2, ranks2, group)

print '[%d] ranks1: %s - trans1: %s' % (MPI.rank,ranks1,tr1)
print '[%d] ranks2: %s - trans2: %s' % (MPI.rank,ranks2,tr2)
print
