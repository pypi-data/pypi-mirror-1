from mpi4py import MPI

mess = "Hello, World!! I am process %d of %d on %s."
info = MPI.rank, MPI.size, MPI.Get_processor_name()
print  mess % info
