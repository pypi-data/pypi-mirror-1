from mpi4py import MPI

def leak_warn():
    o1 = MPI.INT.Dup()
    o2 = MPI.DOUBLE.Dup()
    o1 = None
    o2 = None
    o1 = MPI.COMM_SELF.Get_group()
    o2 = MPI.COMM_WORLD.Get_group()
    o1 = None
    o2 = None
    o1 = MPI.COMM_SELF.Dup()
    o2 = MPI.COMM_WORLD.Dup()
    o1 = None
    o2 = None
    o1 = MPI.Win.Create(None, comm=MPI.COMM_SELF)
    o2 = MPI.Win.Create(None, comm=MPI.COMM_WORLD)
    o1 = None
    o2 = None
    o1 = MPI.COMM_SELF
    o2 = MPI.COMM_WORLD
    o1 = None
    o2 = None


if __name__ == '__main__':
    import sys
    leak_warn()
    sys.stdout.flush()
    sys.stderr.flush()
