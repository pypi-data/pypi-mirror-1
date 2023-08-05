# -*- makefile -*-

.PHONY: default all config src swig build install sdist clean \
	install_home uninstall_home insthome uinsthome distclean

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

clean:
	${PYTHON} setup.py clean --all


install_home:
	${PYTHON} setup.py install --home=${HOME}
insthome: install_home

uninstall_home:
	-${RM} -r ${HOME}/lib/python/$(shell ${PYTHON} setup.py --name)
uinsthome: uninstall_home


distclean: clean 
	-${RM} -r build dist MANIFEST *~
	-cd configure && ${RM} *.pyc *.pyo
	-cd docs && ${MAKE} distclean
