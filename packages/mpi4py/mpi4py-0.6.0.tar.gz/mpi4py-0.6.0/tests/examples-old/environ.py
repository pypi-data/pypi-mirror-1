from mpi4py import MPI

mess = """
VERSION .......... %s
PROCESSOR_NAME ... %s
HOST ............. %s
IO ............... %s
WTIME_IS_GLOBAL .. %s
TAG_UB ........... %s
"""

info = (MPI.Get_version(),
        MPI.Get_processor_name(),
        MPI.HOST,
        MPI.IO,
        MPI.WTIME_IS_GLOBAL,
        MPI.TAG_UB,)
    
print mess % info
