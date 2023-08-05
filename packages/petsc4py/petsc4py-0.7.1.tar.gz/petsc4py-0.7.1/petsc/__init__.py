# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc for Python
================

This package is an interface to PETSc libraries.

PETSc_ is a suite of data structures and routines for the scalable
(parallel) solution of scientific applications modeled by partial
differential equations. It employs the MPI_ standard for all
message-passing communication.

PETSc is intended for use in large-scale application projects, and
several ongoing computational science projects are built around the
PETSc libraries. With strict attention to component interoperability,
PETSc facilitates the integration of independently developed
application modules, which often most naturally employ different
coding styles and data structures.

PETSc is easy to use for beginners. Moreover, its careful design
allows advanced users to have detailed control over the solution
process. PETSc includes an expanding suite of parallel linear and
nonlinear equation solvers that are easily used in application codes
written in C, C++, and Fortran. PETSc provides many of the mechanisms
needed within parallel application codes, such as simple parallel
matrix and vector assembly routines that allow the overlap of
communication and computation. In addition, PETSc includes growing
support for distributed arrays.

.. _PETSc: http://www-unix.mcs.anl.gov/petsc
.. _MPI:   http://www.mpi-forum.org
"""

# --------------------------------------------------------------------

__author__    = 'Lisandro Dalcin'
__credits__   = "PETSc Team <petsc-maint@mcs.anl.gov>"
__version__   = '0.7.1'
__revision__  = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

def init(args=None, arch=None, comm=None):
    """
    Initializes PETSc.

    :Parameters:
      - `args`: command-line arguments, usually the 'sys.argv' list.
      - `arch`: specific configuration to use.
      - `comm`: MPI communicator to use as ``PETSC_COMM_WORLD``. The
        passed communicator **is not** duplicated, so it should not be
        freed before finalization. By default, ``PETSC_COMM_WORLD`` is
        ``MPI_COMM_WORLD``.

    .. note:: This functions should be called only once, typically at
      the beginning or any application. Function ``PetscInitialize()``
      will be actually called the first time the `PETSc` module is
      imported.
    """    
    import petsc4py.lib
    _petsc = petsc4py.lib.Import(arch)
    if args is not None:
        if isinstance(args, str):
            args = str(args).split()
        else:
            args = [str(a) for a in args]
            args = [a for a in args if a]
        if args:
            if args[0].startswith('-'):
                from sys import argv, executable
                progname = None
                if argv and type(argv[0]) is str:
                    progname = argv[0]
                if not progname:
                    progname = executable
                args.insert(0, progname)
            _petsc.PetscSetInitArgs(args)
    if comm is not None:
        _petsc.PetscSetCommWorld(comm)

# --------------------------------------------------------------------

def main(*args):
    """
    Create requested objects and call obj.setFromOptions().
    """
    from petsc4py import PETSc
    #if 'options' in args:
    #    opt = PETSc.Options()
    #    opt.setFromOptions()
    if 'vec' in args:
        vec = PETSc.Vec().create(PETSc.COMM_SELF)
        vec.setSizes(0)
        vec.setFromOptions()
        del vec
    #if 'vecscatter' in args:
    #    i = PETSc.IS().createGeneral([0],PETSc.COMM_SELF)
    #    v = PETSc.Vec().create(PETSc.COMM_SELF)
    #    v.setSizes(1)
    #    v.setType(PETSc.Vec.Type.SEQ)
    #    scatter = PETSc.Scatter().create(v,i,v,i)
    if 'mat' in args:
        mat = PETSc.Mat().create(PETSc.COMM_SELF)
        mat.setSizes(0)
        mat.setFromOptions()
        del mat
    if 'ksp' in args:
        ksp = PETSc.KSP().create(PETSc.COMM_SELF)
        ksp.setFromOptions()
        del ksp
    if 'pc' in args:
        pc = PETSc.PC().create(PETSc.COMM_SELF)
        pc.setFromOptions()
        del pc
    if 'snes' in args:
        snes = PETSc.SNES().create(PETSc.COMM_SELF)
        snes.setFromOptions()
        del snes
    if 'ts' in args:
        ts = PETSc.TS().create(PETSc.COMM_SELF)
        ts.setFromOptions()
        del ts

# --------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    init(sys.argv)
    main(*sys.argv[1:])
    del sys

# --------------------------------------------------------------------
