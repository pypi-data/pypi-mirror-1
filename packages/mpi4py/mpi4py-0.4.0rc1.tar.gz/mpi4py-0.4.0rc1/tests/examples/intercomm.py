from mpi4py import MPI
import sys

# different colors
cmd = """
if MPI.rank < MPI.size/2 :
    color = 0
else:
    color=1"""
MPI.rprint(cmd)
exec cmd
MPI.pprint('[%d] color: %d' % \
           (MPI.rank,color)
           )

# split WORLD communicator in halves
cmd = """
intracomm = MPI.WORLD.Split(color, key=0)"""
MPI.rprint(cmd)
exec cmd
MPI.pprint('[%d] intracomm: rank: %d - size: %d' % \
           (MPI.rank,intracomm.Get_rank(), intracomm.Get_size() )
           )

# input data
cmd = """
input = MPI.rank*11+MPI.size*100"""
MPI.rprint(cmd)
exec cmd
MPI.pprint("[%d] input:  %s" % \
           (MPI.rank, input)
           )

# broadcast data from root to others
cmd = """
root = 0
result = intracomm[root].Bcast(input)"""
MPI.rprint(cmd)
exec cmd
MPI.pprint("[%d] result: %s" % \
           (MPI.rank, result)
           )

# create intercommunicator
cmd = """
local_leader = 0
if MPI.rank < MPI.size/2 :
    remote_leader = MPI.size/2
else:
    remote_leader = 0"""
MPI.rprint(cmd)
exec cmd
MPI.pprint('[%d] leaders: local: %d - remote: %d' % \
           (MPI.rank,local_leader,remote_leader)
           )

cmd = """
intercomm = intracomm.Create_intercomm(local_leader,
                                       MPI.WORLD,
                                       remote_leader)"""
MPI.rprint(cmd)
exec cmd
MPI.pprint('[%d] intercomm: rank: %d - size: %d - remote size: %d' % \
           (MPI.rank,
            intercomm.Get_rank(),
            intercomm.Get_size(),
            intercomm.Get_remote_size(),
            )
           )

# input data
cmd = """
input = MPI.rank*11+MPI.size*100"""
MPI.rprint(cmd)
exec cmd
MPI.pprint("[%d] input:  %s" % \
           (MPI.rank, input)
           )

cmd = """
result = []
if intercomm.Get_rank() == 0:
    result = intercomm.Sendrecv(input,dest=0, source=0)"""
MPI.rprint(cmd)
exec cmd
MPI.pprint("[%d] result: %s" % \
           (MPI.rank, result)
           )

cmd = """
result = intracomm[0].Bcast(result)"""
MPI.rprint(cmd)
exec cmd
MPI.pprint("[%d] result: %s" % \
           (MPI.rank, result)
           )


cmd = """
intracomm.Free()
intercomm.Free()"""
MPI.rprint(cmd)
exec cmd
