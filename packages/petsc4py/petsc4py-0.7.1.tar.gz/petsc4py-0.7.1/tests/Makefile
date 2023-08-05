.PHONY:  default all seq mpi arch


default: seq

all: seq mpi

PYTHON=python

seq:
	@for test_py in `ls test_*.py`; do \
	   echo && echo $$test_py; \
	   ${PYTHON} $$test_py; \
        done

MPIPYTHON=python
MPIEXEC=mpiexec -n
NP=2

mpi:
	@for test_py in `ls *.py`; do \
	  echo && echo $$test_py; \
	  ${MPIEXEC} ${NP} ${MPIPYTHON} $$test_py; \
	done

arch:
	-for ARCH in ${PETSC_DIR}/lib/*; do \
	  PETSC_ARCH=`basename $$ARCH` $(MAKE) ${ACTION}; \
	 done;
