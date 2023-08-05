from mpi4py import MPI

rprint = MPI._rprint
pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

if MPI.size != 4:
    raise Warning, 'run me on 4 procs!!!'
    raise SystemExit

# Graph information
cmd = """
index = [2,3,4,6]
edges = [1,3,0,3,0,2]
reord = False"""
rprint(cmd)
exec cmd

cmd = """
comm = MPI.WORLD.Create_graph(index,edges,reord)"""
rprint(cmd)
exec cmd


if MPI.rank == 0:

    print

    print '[%d] dims: %s - topo: %s' % \
          (MPI.rank, comm.Get_dims(), comm.Get_topo())

    print
    
    for i in xrange(4):
        print "[%d] nngh[%d]: %d - nghs[%d]: %s" % \
              (MPI.rank,
               i, comm.Get_neighbors_count(i),
               i, comm.Get_neighbors(i))
