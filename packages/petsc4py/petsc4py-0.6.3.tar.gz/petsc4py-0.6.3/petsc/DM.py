# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc Application Orderings
===========================

Application Ordering are mappings between an application-centric
ordering (the ordering that is **natural** for the application) and
the parallel ordering that PETSc uses.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['AO',
           'AOBasic',
           'AOMapping',
           ]

# --------------------------------------------------------------------

from petsc4py.lib import _petsc
from petsc4py.lib import _numpy

from petsc4py.Object import Object

# --------------------------------------------------------------------


class AO(Object):

    """
    Abstract PETSc object that manages mappings between different
    global numberings.

    An application ordering ia a mapping between an
    application-centric ordering (the ordering that is *natural* for
    the application) and the parallel ordering that PETSc uses.
    """

    class Type:
        """
        Application Ordering types.
        """
        BASIC    = _petsc.AO_BASIC
        MAPPING  = _petsc.AO_MAPPING

    def __init__(self, *targs, **kwargs):
        super(AO, self).__init__(*targs, **kwargs)
            
    def __call__(self, indices):
        """Same as `ApplicationToPetsc()`."""
        self.ApplicationToPetsc(indices)

    def createBasic(self, app=None, petsc=None, comm=None):
        """
        Creates a basic application ordering.
        """
        if isinstance(app, _petsc._IS) or \
               isinstance(petsc, _petsc._IS):
            return _petsc.AOCreateBasicIS(app, petsc, self)
        else:
            if app is None:
                app = []
            if petsc is not None:
                napp   = _numpy.size(app)
                npetsc = _numpy.size(petsc)
                if napp != npetsc:
                    raise ValueError('incompatible array sizes')
            return _petsc.AOCreateBasic(comm, app, petsc, self)
    
    def createMapping(self, app=None, petsc=None, comm=None):
        """
        Create a basic application mapping.
        """
        if isinstance(app, _petsc._IS) or \
               isinstance(petsc, _petsc._IS):
            return _petsc.AOCreateMappingIS(app, petsc, self)
        else:
            if app is None:
                app = []
            if petsc is not None:
                na = _numpy.size(app)
                np = _numpy.size(petsc)
                if na != np:
                    raise ValueError('incompatible array sizes')
            return _petsc.AOCreateMapping(comm, app, petsc, self)

    def PetscToApplication(self, indices):
        """
        """
        _petsc.AOPetscToApplication(self, indices)

    def ApplicationToPetsc(self, indices):
        """
        """
        _petsc.AOApplicationToPetsc(self, indices)

    def PetscToApplicationPermuteInt(self, array):
        """
        """
        _petsc.AOPetscToApplicationPermuteInt(self, array)

    def ApplicationToPetscPermuteInt(self, array):
        """
        """
        _petsc.AOApplicationToPetscPermuteInt(self, array)

    def PetscToApplicationPermuteReal(self, array):
        """
        """
        _petsc.AOPetscToApplicationPermuteReal(self, array)

    def ApplicationToPetscPermuteReal(self, array):
        """
        """
        _petsc.AOApplicationToPetscPermuteReal(self, array)

    PetscToApp = PetscToApplication
    AppToPetsc = ApplicationToPetsc 


# --------------------------------------------------------------------

class AOBasic(AO):

    """
    Basic application ordering.
    """

    def __init__(self, *targs, **kwargs):
        """See `AO.CreateBasic()`"""
        super(AOBasic, self).__init__(*targs, **kwargs)
        self.createBasic(*targs, **kwargs)
        

class AOMapping(AO):

    """
    Basic application mapping.
    """

    def __init__(self, *targs, **kwargs):
        """See `AO.CreateMapping()`"""
        super(AOMapping, self).__init__(*targs, **kwargs)
        self.createMapping(*targs, **kwargs)


# --------------------------------------------------------------------
