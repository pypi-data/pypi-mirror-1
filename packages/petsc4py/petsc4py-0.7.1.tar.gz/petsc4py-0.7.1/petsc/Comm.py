# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
MPI Communicators
=================

Communicators are the basic objects used by MPI to determine which
processes are involved in a communication.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['Comm',
           'COMM_NULL',
           'COMM_SELF',
           'COMM_WORLD',
           'WORLD_SIZE',
           'WORLD_RANK']

# --------------------------------------------------------------------

from petsc4py.lib import _petsc

# --------------------------------------------------------------------

class CommType(type):
    """
    MPI Communicator metaclass.
    """
    def __init__(mcs, name, bases, dct):
        # initialize base class of this metaclass
        super(CommType, mcs).__init__(name, bases, dct)
        # this part registers this class in C extension module
        # for easy access of type objects in the C side
        reg_name = name + 'TypeRegister'
        reg_func = getattr(_petsc, reg_name, None)
        if reg_func is not None:
            reg_func(mcs)
            delattr(_petsc, reg_name)
        # type registration
        if not hasattr(_petsc, '_' + name):
            setattr(_petsc, '_' + name, mcs)

# --------------------------------------------------------------------

class Comm(_petsc.Comm):

    """
    MPI Communicator.
    """
    
    __metaclass__ = CommType

    def __init__(self, *targs, **kwargs):
        super(Comm, self).__init__(*targs, **kwargs)
        if targs or kwargs:
            _petsc.PetscCommSetComm(self, *targs, **kwargs)
        
    def destroy(self):
        """
        Free a communicator.

        .. note:: Use this method with care
        """
        _petsc.PetscCommDestroy(self)

    def duplicate(self):
        """
        Duplicate the communicator only if it is not already a PETSc
        communicator.

        .. note:: PETSc communicators are just regular MPI
           communicators that keep track of which tags have been used
           to prevent tag conflict. If you pass a non-PETSc
           communicator into a PETSc creation routine it will attach a
           private communicator for use in the objects communications.
        """
        return _petsc.PetscCommDuplicate(self)

    def getSize(self):
        """
        Return the communicator size.
        """
        return _petsc.PetscCommGetSize(self)
    
    def getRank(self):
        """
        Return the processor rank in a communicator.
        """
        return _petsc.PetscCommGetRank(self)

    def barrier(self):
        """
        Block until this routine is executed by all processors.
        """
        _petsc.PetscCommBarrier(self)

    def globalMin(self, local):
        """
        Compute the minimum (real) value over several processors.
        """
        return _petsc.PetscGlobalMin(local, self)

    def globalMax(self, local):
        """
        Compute the maximum (real) value over several processors.
        """
        return _petsc.PetscGlobalMax(local, self)                

    def globalSum(self, local):
        """
        Compute the (scalar) sum over several processors.
        """
        return _petsc.PetscGlobalSum(local, self)

        
    size = property(getSize)
    rank = property(getRank)

# --------------------------------------------------------------------

COMM_NULL  = _petsc.PetscGetCommNull()
"""``COMM_NULL`` communicator"""

COMM_SELF  = _petsc.PetscGetCommSelf()
"""``COMM_SELF`` communicator"""

COMM_WORLD = _petsc.PetscGetCommWorld()
"""``COMM_WORLD`` communicator"""

WORLD_SIZE = COMM_WORLD.getSize()
"""Size of `COMM_WORLD`"""

WORLD_RANK = COMM_WORLD.getRank()
"""Rank of this processor in `COMM_WORLD`"""

# --------------------------------------------------------------------
