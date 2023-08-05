# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc Random
============

Random numbers generator.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['Random']

# --------------------------------------------------------------------

from petsc4py.lib import _petsc

from petsc4py.Object import Object

# --------------------------------------------------------------------


class Random(Object):

    """
    Abstract PETSc object that manages generating random numbers.

    .. note:: By default, random numbers are generated via
       srand48()/drand48() that are uniformly distributed over [0,1).
       The user can shift and stretch this interval by calling
       `setInterval()`.

    .. tip:: Use `Vec.setRandom()` to set the elements of a vector to
       random numbers.
    """

    class Type:
        """
        Random number generator types

        Currently three types of random numbers are supported. These
        types are equivalent when working with real numbers:
        
        - `DEFAULT`: both real and imaginary components are random.
        - `REAL`:real component is random, imaginary component is 0.
        - `IMAGINARY`: imaginary component is random, real component
          is 0.
        """
        # native
        PETSCRAND   = _petsc.PETSCRAND
        PETSCRAND48 = _petsc.PETSCRAND48
        SPRNG       = _petsc.SPRNG
        # aliases
        RAND   = PETSCRAND
        RAND48 = PETSCRAND48
        
    def __init__(self, *targs, **kwargs):
        super(Random, self).__init__(*targs, **kwargs)

    def __call__(self):
        """Same as `getValue()`"""
        return self.getValue()

    def create(self, comm=None):
        """
        Creates a context for generating random numbers, and
        initializes the random-number generator.
        """
        return _petsc.PetscRandomCreate(comm, self)

    def getValue(self):
        """
        Generates and returns a random number.
        """
        return _petsc.PetscRandomGetValue(self)

    def getValueReal(self):
        """
        Generates and returns a random number.
        """
        return _petsc.PetscRandomGetValueReal(self)

    def getValueImaginary(self):
        """
        Generates and returns a random number.
        """
        return _petsc.PetscRandomGetValueImaginary(self)

    def getSeed(self):
        """
        Gets the random seed.
        """
        return _petsc.PetscRandomGetSeed(self)
    
    def setSeed(self, seed):
        """
        Sets the random seed and seeds the generator.
        """
        _petsc.PetscRandomSetSeed(self, seed)
        _petsc.PetscRandomSeed(self)

    def getInterval(self):
        """
        Gets the interval over which the random numbers will be
        randomly distributed.  By default, this interval is [0,1).

        :Return:
          - the interval '[low,high)' (as a tuple) over which the
            random numbers will be randomly distributed.  By
            default, this interval is [0,1).
        """
        return tuple(_petsc.PetscRandomGetInterval(self))

    def setInterval(self, interval):
        """
        Sets the interval '[low,high)' over which the random numbers
        will be randomly distributed.  By default, this interval is
        [0,1).

        :Parameters:
          - `interval`: sequence with the interval over which the
            random numbers will be randomly distributed.
        """
        low, high = interval
        _petsc.PetscRandomSetInterval(self, low, high)

    seed     = property(getSeed, setSeed)
    interval = property(getInterval, setInterval)


# --------------------------------------------------------------------
