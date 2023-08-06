# -*- makefile -*-

.PHONY: default config build test install sdist clean \
	install_home uninstall_home insthome uinsthome distclean

PYTHON = python

default: build

config: 
	${PYTHON} setup.py config ${CONFIGOPT}

build:
	${PYTHON} setup.py build ${BUILDOPT}

test:
	${MPIEXEC} ${PYTHON} tests/unittest/alltest.py

install: build
	su -c '${PYTHON} setup.py install ${INSTALLOPT}'

sdist:
	${PYTHON} setup.py sdist ${SDISTOPT}

clean:
	${PYTHON} setup.py clean --all
	-${RM} _configtest.* *.py[co]
	-${MAKE} -C docs clean


insthome: install_home
install_home: build
	${PYTHON} setup.py install --home=${HOME}

uinsthome: uninstall_home
uninstall_home:
	-${RM} -r ${HOME}/lib/python/mpi4py
	-${RM} -r ${HOME}/lib/python/mpi4py-*-py*.egg-info

distclean: clean 
	-${RM} -r build  *.py[co]
	-${RM} -r MANIFEST dist mpi4py.egg-info
	-${MAKE} -C docs distclean
	-${RM} `find . -name '*~'`
	-${RM} `find . -name '*.py[co]'`
