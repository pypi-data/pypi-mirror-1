# -*- makefile -*-

.PHONY: default tree-arch config src swig build install \
	home_install home_uninstall \
        install_home uninstall_home \
        insthome uinsthome \
	sdist \
	clean distclean

PYTHON=python
PACKAGE=petsc4py

default: build

tree-arch:
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

home_install:
	${PYTHON} setup.py install --home=${HOME}
install_home: home_install
insthome: home_install

home_uninstall:
	-${RM} -r ${HOME}/lib/python/$(shell ${PYTHON} setup.py --name)
uninstall_home: home_uninstall
uinsthome:  home_uninstall


clean:
	${PYTHON} setup.py clean --all

distclean: clean
	-${RM} -r build dist MANIFEST *~
	-cd configure && ${RM} *.pyc *.pyo
	-cd docs && ${MAKE} distclean
