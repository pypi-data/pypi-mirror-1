.PHONY: default all seq mpi mpi-n-1 mpi-n-x alltest clean distclean

PYTHON  = python
MPIEXEC = mpiexec
HOSTS   =
NPFLAG  = -n
NP      = 3

default: seq

all: seq mpi


seq:
	${MAKE} MPIEXEC= HOSTS= NPFLAG= NP= alltest

mpi: mpi-n-1 mpi-n-x

mpi-n-1:
	${MAKE} NP=1 alltest

mpi-n-x:
	${MAKE} alltest


alltest:
	-for i in `ls test_*.py`; do \
	    echo; echo ${MPIEXEC} ${HOSTS} ${NPFLAG} ${NP} ${PYTHON} $$i; \
	    ${MPIEXEC} ${HOSTS} ${NPFLAG} ${NP} ${PYTHON} $$i; \
	done

clean:

distclean: clean
