# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Index Sets (IS)
===============

Index Sets are used to index into vectors and matrices and to setup
vector scatters.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['IS',
           'ISGeneral',
           'ISBlock',
           'ISStride',

           'LGMapping',
           ]

# --------------------------------------------------------------------

from petsc4py.lib import _petsc
from petsc4py.lib import _numpy

from petsc4py.Object import Object

# --------------------------------------------------------------------


class IS(Object):

    """
    Abstract PETSc object for indexing.

    An index set is a generalization of a subset of integers. They are
    used for defining application orderings, vector scatters and
    gathers, matrix orderings, permutations, etc.

    .. note:: When the communicator is not `COMM_SELF`, the operations
       on `IS` are NOT conceptually the same as ``MPI_Group``
       operations. The `IS` are then distributed sets of indices and
       thus certain operations on them are collective.
    """

    class Type:
        """
        IS types.
        """
        GENERAL = _petsc.IS_GENERAL
        STRIDE  = _petsc.IS_STRIDE
        BLOCK   = _petsc.IS_BLOCK

    def __init__(self, *targs, **kwargs):
        super(IS, self).__init__(*targs, **kwargs)
        
    def __len__(self):
        """local index set length"""
        return _petsc.ISGetLocalSize(self)

    def __array__(self, dtype=None):
        """
        Return an array that contains this processor's portion of the
        indices. This method makes a copy.
        """
        idtype = _petsc.PetscInt
        lsize = _petsc.ISGetLocalSize(self)
        indices = _numpy.empty(lsize, idtype)
        _petsc.ISGetIndices(self, indices)
        if dtype is not None:
            indices = indices.astype(dtype)
        return indices

    def createGeneral(self, indices, comm=None):
        """
        Create an index set containing a general list of integers.

        :Parameters:
          - `indices`: Array of integers.
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).

        :Returns:
          - the created index set.
        """
        return _petsc.ISCreateGeneral(comm, indices, self)

    def createBlock(self, indices, bsize, comm=None):
        """
        Create an block index set containing a list of integers and a
        block size. The indices are relative to entries, not blocks.
        
        :Parameters:
          - `indices`: Array of integers.
          - `bsize`: Number of elements in each block (defaults to 1).
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).

        :Returns:
          - the created index set.

        .. tip:: If you wish to index the values [0,1,4,5], then use a
           block size of 2 and indices of [0,4].
        """
        bsize = _petsc.obj_bsize(bsize, 1)
        return _petsc.ISCreateBlock(comm, bsize, indices, self)

    def createStride(self, size, first=None, step=None, comm=None):
        """
        Create an stride index set containing a list of evenly spaced
        integers.

        :Parameters:
          - `size`: length of the index set..
          - `first`: first element of the index set (defaults to 0).
          - `step`: change to the next index (defaults to 1).
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).

        :Returns:
          - the created index set.
        """
        if not isinstance(size, int):
            raise TypeError("'size' must be integer")
        elif size < 0:
            raise ValueError("'size' must be nonnegative")
        if first is None:
            first = 0
        elif not isinstance(first, int):
            raise TypeError("'first' must be integer")
        if step is None:
            step = 1
        elif not isinstance(step, int):
            raise TypeError("'step' must be integer")
        return _petsc.ISCreateStride(comm, size, first, step, self)

    def duplicate(self):
        """
        Creates a duplicate copy of an index set.

        :Returns:
          - the duplicated index set.
        """
        return _petsc.ISDuplicate(self)

    def getSize(self):
        """
        Returns the global length of an index set.
        """
        return _petsc.ISGetSize(self)

    def getLocalSize(self):
        """
        Returns the local length of an index set.
        """
        return _petsc.ISGetLocalSize(self)

    def getSizes(self):
        """
        Returns the local and global lengths of an index set.
        """
        return _petsc.ISGetLocalSize(self), _petsc.ISGetSize(self)

    def getSizeBlock(self):
        """
        Returns the number of blocks in a block index set.
        """
        return _petsc.ISBlockGetSize(self)

    def getBlockSize(self):
        """
        Returns the number of elements in a block for a block index
        set.
        """
        return _petsc.ISBlockGetBlockSize(self)

    def getIndices(self, indices=None):
        """
        Returns the indices stored in the index set
        """
        if indices is None:
            lsize   = _petsc.ISGetLocalSize(self)
            indices = _numpy.empty(lsize, _petsc.PetscInt)
        _petsc.ISGetIndices(self, indices)
        return indices

    def isPermutation(self):
        """
        Determines whether the index set has been declared to be a
        permutation.
        """
        return bool(_petsc.ISPermutation(self))

    def setPermutation(self):
        """
        Informs the index set that it is a permutation.
        """
        return _petsc.ISSetPermutation(self)

    def isIdentity(self):
        """
        Determines whether index set is the identity mapping.
        """
        return bool(_petsc.ISIdentity(self))

    def setIdentity(self):
        """
        Informs the index set that it is an identity.
        """
        _petsc.ISSetIdentity(self)

    def invertPermutation(self, nlocal=None):
        """
        Creates a new permutation that is the inverse of
        a given permutation.

        :Parameters:
          - `nlocal`: number of indices on this processor in result
            (ignored for 1 proccessor) or use `DECIDE`.

        :Returns:
          - the inverse permutation.

        .. note:: For parallel index sets this does the complete
           parallel permutation, but the code is not efficient for
           huge index sets (10,000,000 indices).
        """
        if nlocal is None:
            nlocal = _petsc.PETSC_DECIDE
        elif nlocal != _petsc.PETSC_DECIDE:
            if not isinstance(nlocal, int):
                raise TypeError("'nlocal' must be integer")
            elif nlocal < 0:
                raise ValueError("'nlocal' must be nonnegative")
        return _petsc.ISInvertPermutation(self, nlocal)

    def equal(self, iset):
        """
        Compares if two index sets have the same set of indices.
        """
        return bool(_petsc.ISEqual(self, iset))

    def sort(self):
        """
        Sorts the indices of an index set.
        """
        _petsc.ISSort(self)

    def isSorted(self):
        """
        Checks the indices to determine whether they have been sorted.

        .. note::
           For parallel index sets this only indicates if the local
           part of the index set is sorted. So some processors may
           return 'True` while others may return 'False'.
        """
        return bool(_petsc.ISSorted(self))

    def sum(self, iset):
        """
        Computes the sum (union) of two index sets in place.

        .. note:: If ``n1`` and ``n2`` are the sizes of the sets, this
           takes ``O(n1+n2)`` time; if `iset` is a subset of `self`,
           `self` is left unchanged, otherwise `self` is
           reallocated. Both index sets need to be sorted on input.
        """
        _petsc.ISSum(self, iset)

    def expand(self, iset):
        """
        Computes the sum (union) of two index sets.

        .. note:: Negative values are removed from the lists. This
           requires O(imax-imin) memory and O(imax-imin) work, where
           imin and imax are the bounds on the indices in `self` and
           `iset`.
        """
        return _petsc.ISExpand(self, iset)
        
    def difference(self, iset):
        """
        Computes the difference between two index sets.

        .. note:: Negative values are removed from the lists. `iset`
           may have values that are not in `self`. This requires
           O(imax-imin) memory and O(imax-imin) work, where imin and
           imax are the bounds on the indices in `self`.
        """
        return _petsc.ISDifference(self, iset)

    def allGather(self):
        """
        Given an index set on each processor, generates a large index
        set (same on each processor) by concatenating together each
        processors index set.

        .. note:: index set on each processor must be created with a
           common communicator (e.g., `COMM_WORLD`). If the index sets
           were created with `COMM_SELF`, this routine will not work
           as expected, since each process will generate its own new
           index set that consists only of itself.

        .. note:: `IS.allGather()` is clearly not scalable for large
           index sets.
        """
        return _petsc.ISAllGather(self)

    size  = property(getSize)
    sizes = property(getSizes)
    lsize = local_size  = property(getLocalSize)
    gsize = global_size = property(getSize)
    bsize = block_size  = property(getBlockSize)
    
    indices = array = property(getIndices)

    permutation = property(isPermutation, setPermutation)
    identity    = property(isIdentity, setIdentity)
    sorted      = property(isSorted)

    
class ISGeneral(IS):

    """
    Index set containing a general list of integers.
    """
    
    def __init__(self, *targs, **kwargs):
        """See `IS.createGeneral()`"""
        super(ISGeneral, self).__init__(*targs, **kwargs)
        self.createGeneral(*targs, **kwargs)


class ISBlock(IS):

    """
    Index set containing a list of integers and a block size.
    """
    
    def __init__(self, *targs, **kwargs):
        """See `IS.createBlock()`"""
        super(ISBlock, self).__init__(*targs, **kwargs)
        self.createBlock(*targs, **kwargs)


class ISStride(IS):

    """
    Index set containing a list of evenly spaced integers.
    """
    
    def __init__(self, *targs, **kwargs):
        """See `IS.createStride()`"""
        super(ISStride, self).__init__(*targs, **kwargs)
        self.createStride(*targs, **kwargs)
        
    def toGeneral(self):
        """
        Converts a stride index set to a general index set.
        """
        _petsc.ISStrideToGeneral(self)
        
    def getInfo(self):
        """
        Returns the first index in a stride index set and the stride
        width.
        """
        return tuple(_petsc.ISStrideGetInfo(self))


# --------------------------------------------------------------------


class LGMapping(Object):

    """
    Mapping from an arbitrary local ordering from 0 to n-1 to a global
    ordering used by a vector or matrix.
    """

    class GLMapType:
        """
        Global to local mapping type.

        - `MASK`:  missing global indices are replaced with -1.
        - `DROP`:  missing global indices are dropped.
        """
        MASK = _petsc.IS_GTOLM_MASK
        DROP = _petsc.IS_GTOLM_DROP
    
    def __init__(self, *targs, **kwargs):
        """See `create()`"""
        super(LGMapping, self).__init__(*targs, **kwargs)
        if targs or kwargs:
            self.create(*targs, **kwargs)
        
    def __len__(self):
        """Same as `getSize()`"""
        return self.getSize()

    def __call__(self, indices, result=None):
        """Same as `apply()`."""
        return self.apply(indices, result)

    def create(self, indices, comm=None):
        """
        Creates a mapping between a local (0 to n) ordering and a
        global parallel ordering.

        :Parameters:
          - `indices`: array or `IS` index set with the global index
            for each local element.
          - `comm`: MPI communicator (usually `COMM_WORLD`). This
            argument is ignored when `indices` is an index set.

        :Returns:
          - the created local to global mapping.
        """
        if isinstance(indices, IS):
            return _petsc.LGMappingCreateIS(indices, self)
        else:
            return _petsc.LGMappingCreate(comm, indices, self)

    def createBlock(self, lgmap, bsize):
        """
        Creates a blocked index version of an LGMapping that is appropriate
        for `Vec.setLGMappingBlock()` and `Mat.setLGMappingBlock()`.

        :Parameters:
          - `lgmap`: base local to global mapping.
          - `bsize`: block size.
        """
        bsize = _petsc.obj_bsize(bsize)
        return _petsc.LGMappingBlock(lgmap, bsize, self)
    
    def getSize(self):
        """
        Gets the local size of a local to global mapping.
        """
        return _petsc.LGMappingGetSize(self)

    def getInfo(self):
        """
        Gets the neighbor information for each processor and each
        index shared by more than one processor

        :Returns:
            - dictionary where **keys** are neighboring processors
              that are connected to this one and **values** are
              indices of local nodes in local numbering shared with
              neighbor (sorted by global numbering).

        .. note:: In the uniprocessor case, returned dictionary is
           empty.
        """
        neighs, nodes = _petsc.LGMappingGetInfo(self)
        return dict((n, nodes[i]) for i, n in enumerate(neighs))

    def apply(self, indices, result=None):
        """
        Takes a list of integers in a local numbering and converts
        them to the global numbering.

        :Parameters:
           - `indices`: input array with indices in local numbering.
           - `result`: array to store the global numbering. It can be
             the same array as `indices`. if it is `None`, a new array
             is allocated.

        :Returns:
           - the array with global numbering.
        """
        if isinstance(indices, IS):
            return _petsc.LGMappingApplyIS(self, indices)
        else:
            indices = _numpy.asarray(indices, _petsc.PetscInt)
            if result is None:
                result = _numpy.empty(_numpy.shape(indices),
                                      _petsc.PetscInt)
            else:
                assert isinstance(result, _numpy.ndarray)
                assert _numpy.shape(indices) == _numpy.shape(result)
            _petsc.LGMappingApply(self, (indices, result))
            return result

    def applyInverse(self, indices, map_type=None):
        """
        Provides the local numbering for a list of integers specified
        with a global numbering.
        """
        map_type = _petsc.get_attr(LGMapping.GLMapType, map_type)
        return _petsc.LGMappingApplyInverse(self, map_type, indices)

    size = property(getSize)
    info = property(getInfo)

# --------------------------------------------------------------------
