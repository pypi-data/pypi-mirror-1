# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc Error.
===========

Exception class for PETSc runtime errors in the C side.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['Error']

# --------------------------------------------------------------------

import sys as _sys
from petsc4py.lib import _petsc

# --------------------------------------------------------------------

class Error(RuntimeError):

    """
    PETSc Error.
    """

    ## def __init__(self, ierr=0, msg=None):
    ##     txt, _ = PetscErrorMessage(ierr)
    ##     RuntimeError.__init__(self, ierr, txt, msg)

    @staticmethod
    def getTraceBack():
        """
        Gets a list of strings with traceback information
        about PETSc runtime errors originated in the C side.
        """
        return list(_petsc.PetscTraceBackError)

    @staticmethod
    def view():
        """
        Displays (in sys.stderr) traceback information about PETSc
        runtime errors originated in the C side.
        """
        comm_self = _petsc.PetscGetCommSelf()
        comm_world = _petsc.PetscGetCommWorld()
        wsize = _petsc.PetscCommGetSize(comm_world)
        wrank = _petsc.PetscCommGetRank(comm_world)
        for error in _petsc.PetscTraceBackError:
            message = '[%*d] %s\n' % (len(str(wsize-1)), wrank, error)
            _petsc.PetscFPrintf(comm_self, _sys.stderr, message)

# --------------------------------------------------------------------

_petsc.PetscSetExceptionClass(Error)

# --------------------------------------------------------------------
