# -*- makefile -*-

.PHONY: default all config src swig build install sdist clean \
	install_home uninstall_home insthome uinsthome distclean

PYTHON=python

default: build

all:
	-for ARCH in ${PETSC_DIR}/lib/*; do \
	  PETSC_ARCH=`basename $$ARCH` $(MAKE) ${ACTION}; \
	 done;

config: 
	${PYTHON} setup.py config

src:
	${PYTHON} setup.py build_src

swig:
	${PYTHON} setup.py build_src --force

build:
	${PYTHON} setup.py build

install: build
	su -c '${PYTHON} setup.py install'

sdist:
	${PYTHON} setup.py sdist

clean:
	${PYTHON} setup.py clean --all


insthome: install_home
install_home:
	${PYTHON} setup.py install --home=${HOME}


PACKAGE=petsc4py
uinsthome: uninstall_home
uninstall_home:
	-${RM} -r ${HOME}/lib/python/${PACKAGE}

distclean: clean 
	-${RM} -r build MANIFEST dist *~
	-cd configure && ${RM} *.pyc *.pyo
	-cd docs && ${MAKE} distclean

