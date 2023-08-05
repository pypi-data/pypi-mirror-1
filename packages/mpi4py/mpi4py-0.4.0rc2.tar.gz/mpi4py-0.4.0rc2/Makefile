# -*- makefile -*-

.PHONY: default config build install install_home uninstall_home insthome uinsthome sdist clean distclean

PYTHON = python

BUILDOPT=

default: build

config: 
	${PYTHON} setup.py config

build:
	${PYTHON} setup.py build ${BUILDOPT}

install: build
	su -c '${PYTHON} setup.py install'

insthome: install_home
install_home: build
	${PYTHON} setup.py install --home=${HOME}

uinsthome: uninstall_home
uninstall_home:
	-${RM} -r ${HOME}/lib/python/mpi4py

sdist:
	${PYTHON} setup.py sdist

clean:
	${PYTHON} setup.py clean --all
	-${RM} _configtest.*
	-cd docs && ${MAKE} clean

distclean: clean 
	-${RM} `find . -name '*~'`
	-${RM} -r MANIFEST build dist *.egg-info *.py[co]
	-cd docs && ${MAKE} distclean
