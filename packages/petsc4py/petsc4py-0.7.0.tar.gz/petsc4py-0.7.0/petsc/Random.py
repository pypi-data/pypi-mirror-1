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

__all__ = ['Random',
           ]

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

    class Type(object):
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
        def __init__(self, rnd_type):
            self._rnd_type = rnd_type
        def __call__(self, name, bases, dct):
            klass = type(Random)(name, bases, dct)
            def __init__(self, rnd=None, *targs, **kwargs):
                """See `Random.create()` and Random.setType()."""
                super(Random, self).__init__(*targs, **kwargs)
                rnd_type = getattr(type(self), 'TYPE', None)
                if isinstance(rnd, Random):
                    _petsc.Random_init(self, rnd, rnd_type)
                else:
                    comm = rnd
                    _petsc.PetscRandomCreate(comm, self)
                    if rnd_type is not None:
                        _petsc.PetscRandomSetType(self, rnd_type)
            setattr(klass, 'TYPE', self._rnd_type)
            setattr(klass, '__init__', __init__)
            return klass
        
    def __init__(self, *targs, **kwargs):
        super(Random, self).__init__(*targs, **kwargs)

    def __call__(self):
        """Same as `getValue()`"""
        return _petsc.PetscRandomGetValue(self)

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

class RandomRAND(Random):
    """
    Random implementation based on rand().
    """
    __metaclass__ = Random.Type(Random.Type.RAND)

class RandomRAND48(Random):
    """
    Random implementation based on rand48().
    """
    __metaclass__ = Random.Type(Random.Type.RAND48)

class RandomSPRNG(Random):
    """
    Random implementation based on SPRNG library.
    """
    __metaclass__ = Random.Type(Random.Type.SPRNG)

# --------------------------------------------------------------------
