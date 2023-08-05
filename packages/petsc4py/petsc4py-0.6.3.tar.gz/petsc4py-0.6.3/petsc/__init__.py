# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc for Python
================

This is an interface to PETSc libraries.

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
__date__      = '15 September 2005'
__version__   = '0.6.2'
__revision__  = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

def init(args=None, arch=None, comm=None):
    """
    Initializes PETSc.

    :Parameters:
      - 'args': Command-line arguments, usually the 'sys.argv' list.
      - `arch`: Specific configuration to use.
      - `comm`: MPI communicator to use as ``PETSC_COMM_WORLD``. The
        passed communicator **is not** duplicated, so it should not be
        freed before finalization. By default, ``PETSC_COMM_WORLD`` is
        ``MPI_COMM_WORLD``.

    ..note::
      ``PetscInitialize()`` will be actually called the first
      time `PETSc` module is imported.
    """    
    import petsc4py.lib
    _petsc = petsc4py.lib.Import(arch)
    if args is not None:
        args = list(args)
        if args and (type(args[0]) is str) \
               and args[0] and (args[0][0] == '-'):
            from sys import argv
            if argv and type(argv[0]) is str:
                progname = argv[0]
            else:
                progname = 'Unknown Name'
            args.insert(0, progname)
        _petsc.PetscSetArgs(args)
    if comm is not None:
        _petsc.PetscSetCommWorld(comm)

# --------------------------------------------------------------------
