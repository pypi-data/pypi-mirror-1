from mpi4py import MPI

if MPI.size != 4:
    raiseSystemExit, 'please, run me on 4 processors...'

# Graph information
cmd = """
index = [2,3,4,6]
edges = [1,3,0,3,0,2]
reord = False"""
MPI.rprint(cmd)
exec cmd

cmd = """
comm = MPI.WORLD.Create_graph(index,edges,reord)"""
MPI.rprint(cmd)
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
