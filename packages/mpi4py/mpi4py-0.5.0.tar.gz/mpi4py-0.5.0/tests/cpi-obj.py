#!/bin/env python
"""
Parallel PI computation using Collective Communications
of general Python objects.

usage::

  $ mpiexec -n <nprocs> cpi-obj.py
"""

from mpi4py import MPI
from math   import pi as PI

def get_n():
    prompt  = "Enter the number of intervals: (0 quits) "
    try:
        n = int(raw_input(prompt));
        if n < 0: n = 0
    except:
        n = 0
    return n

def comp_pi(n, myrank=0, nprocs=1):
    h = 1.0 / n;
    s = 0.0;
    for i in xrange(myrank + 1, n + 1, nprocs):
        x = h * (i - 0.5);
        s += 4.0 / (1.0 + x**2);
    return s * h

def prn_pi(pi, PI):
    import sys
    message = "pi is approximately %.16f, error is %.16f\n"
    sys.stdout.write(message % (pi, abs(pi - PI)))

comm = MPI.COMM_WORLD
nprocs = comm.Get_size()
myrank = comm.Get_rank()

while True:
    if myrank == 0:
        n = get_n()
    else:
        n = None
    n = comm.Bcast(n, root=0)
    if n == 0:
        break
    mypi = comp_pi(n, myrank, nprocs)
    pi = comm.Reduce(mypi, root=0, op=MPI.SUM)
    if myrank == 0:
        prn_pi(pi, PI)
