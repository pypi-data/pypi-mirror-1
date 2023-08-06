.PHONY: all base inter topo clean distclean

PYTHON  = python
MPIEXEC = mpirun

all: base inter topo

base:
	for i in `ls *.py |grep -v comm`; do \
	    echo; \
	    echo ${MPIEXEC} -np 5 ${PYTHON} $$i; \
	    ${MPIEXEC} -np 5 ${PYTHON} $$i; \
	done

inter:
	${MPIEXEC} -np  4 ${PYTHON} intercomm.py

topo:
	${MPIEXEC} -np  4 ${PYTHON} graphcomm.py
	${MPIEXEC} -np 12 ${PYTHON} cartcomm.py

clean:

distclean: clean
