from mpi4py import MPI

MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

if MPI.size != 12:
    raise Warning, 'run me with 12 procs !!!'
    raise SystemExit

dims = (2,3,2)
periods = (False,)*3
reord = False

comm = MPI.WORLD.Create_cart(dims,periods,reord)


print '[%d]' % MPI.rank, 'dim:   ', comm.Get_dim()
print '[%d]' % MPI.rank, 'topo:  ', comm.Get_topo()
print '[%d]' % MPI.rank, 'rank:  ', comm.Get_cart_rank(comm.Get_coords(MPI.rank))
print '[%d]' % MPI.rank, 'coords:', comm.Get_coords(MPI.rank)
print ''

import sys
sys.stdout.flush()

