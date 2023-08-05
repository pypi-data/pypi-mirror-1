from mpi4py import MPI
import sys

rprint = MPI._rprint
pprint = MPI._pprint
MPI.size = MPI.WORLD_SIZE
MPI.rank = MPI.WORLD_RANK

if MPI.size != 4:
    raise Warning, 'run me on 4 procs!!!'
    raise SystemExit

# different colors
cmd = """
if MPI.rank < MPI.size/2 :
    color = 0
else:
    color=1"""
rprint(cmd)
exec cmd
pprint('[%d] color: %d' % \
       (MPI.rank,color)
       )

# split WORLD communicator in halves
cmd = """
intracomm = MPI.WORLD.Split(color, key=0)"""
rprint(cmd)
exec cmd
pprint('[%d] intracomm: rank: %d - size: %d' % \
       (MPI.rank,intracomm.Get_rank(), intracomm.Get_size() )
       )

# input data
cmd = """
input = MPI.rank*11+MPI.size*100"""
rprint(cmd)
exec cmd
pprint("[%d] input:  %s" % \
       (MPI.rank, input)
       )

# broadcast data from root to others
cmd = """
root = 0
result = intracomm[root].Bcast(input)"""
rprint(cmd)
exec cmd
pprint("[%d] result: %s" % \
       (MPI.rank, result)
       )

# create intercommunicator
cmd = """
local_leader = 0
if MPI.rank < MPI.size/2 :
    remote_leader = MPI.size/2
else:
    remote_leader = 0"""
rprint(cmd)
exec cmd
pprint('[%d] leaders: local: %d - remote: %d' % \
       (MPI.rank,local_leader,remote_leader)
       )

cmd = """
intercomm = intracomm.Create_intercomm(local_leader,
                                       MPI.WORLD,
                                       remote_leader)"""
rprint(cmd)
exec cmd
pprint('[%d] intercomm: rank: %d - size: %d - remote size: %d' % \
       (MPI.rank,
        intercomm.Get_rank(),
        intercomm.Get_size(),
        intercomm.Get_remote_size(),
        )
       )

# input data
cmd = """
input = MPI.rank*11+MPI.size*100"""
rprint(cmd)
exec cmd
pprint("[%d] input:  %s" % \
       (MPI.rank, input)
       )

cmd = """
result = []
if intercomm.Get_rank() == 0:
    result = intercomm.Sendrecv(input,dest=0, source=0)"""
rprint(cmd)
exec cmd
pprint("[%d] result: %s" % \
       (MPI.rank, result)
       )

cmd = """
result = intracomm[0].Bcast(result)"""
rprint(cmd)
exec cmd
pprint("[%d] result: %s" % \
       (MPI.rank, result)
       )


cmd = """
intracomm.Free()
intercomm.Free()"""
rprint(cmd)
exec cmd
