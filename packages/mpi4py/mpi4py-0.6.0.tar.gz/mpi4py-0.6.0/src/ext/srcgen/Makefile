# -*- makefile -*-

.PHONY: all libmpi swig

all: libmpi swig

libmpi:
	python apigen.py -o ..

swig:
	swig -python -O -noproxy -o ../mpi_swig.c mpi_swig.i
