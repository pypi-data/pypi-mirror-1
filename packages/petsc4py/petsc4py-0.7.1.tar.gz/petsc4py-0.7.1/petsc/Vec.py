# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Vectors (Vec)
=============

Vectors provide operations required for setting up and solving
large-scale linear and nonlinear problems. Includes easy-to-use
parallel scatter and gather operations, as well as special-purpose
code for handling ghost points for regular data structures.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['Vec',
           'VecSeq',
           'VecMPI',
           'VecShared',
           'VecSieve',

           'Scatter',
           ]

# --------------------------------------------------------------------

from petsc4py.lib import _petsc
from petsc4py.lib import _vecops
from petsc4py.lib import _numpy

from petsc4py.Object import Object

# --------------------------------------------------------------------


class Vec(Object):

    """
    Abstract PETSc vector object.
    """

    class Type(object):
        """
        Vec types.
        """
        SEQ    = _petsc.VECSEQ
        MPI    = _petsc.VECMPI
        FETI   = _petsc.VECFETI
        SHARED = _petsc.VECSHARED
        SIEVE  = _petsc.VECSIEVE
        def __init__(self, vec_type):
            self._vec_type = vec_type
        def __call__(self, name, bases, dct):
            klass = type(Vec)(name, bases, dct)
            setattr(klass, 'TYPE', self._vec_type)
            if '__init__' not in dct:
                def __init__(self, vec=None, *targs, **kwargs):
                    """See `Vec.create()` and Vec.setType()."""
                    super(Vec, self).__init__(*targs, **kwargs)
                    vec_type = getattr(type(self), 'TYPE', None)
                    _petsc.Vec_init(self, vec, vec_type)
                setattr(klass, '__init__', __init__)
            return klass

    class Option:
        """
        Vector options
        """
        IGNORE_OFF_PROC_ENTRIES = _petsc.VEC_IGNORE_OFF_PROC_ENTRIES
        TREAT_OFF_PROC_ENTRIES  = _petsc.VEC_TREAT_OFF_PROC_ENTRIES

    def __init__(self, *targs, **kwargs):
        super(Vec, self).__init__(*targs, **kwargs)
        
    def __len__(self):
        """local vector length"""
        return _petsc.VecGetLocalSize(self)
    
    def __iter__(self):
        """iterate over local values"""
        start, end = _petsc.VecGetOwnershipRange(self)
        get_value  = _petsc.VecGetValue
        for i in xrange(start, end):
            yield get_value(self, i)

    def __getitem__(self, i):
        """Similar to `getValue()`/`getValues()`"""
        if isinstance(i, int):
            return self.getValue(i)
        if isinstance(i, slice):
            dtype  = _petsc.PetscInt
            vsize  = _petsc.VecGetSize(self)
            start, stop, stride = i.indices(vsize)
            i = _numpy.arange(start, stop, stride, dtype)
        return self.getValues(i)

    def __setitem__(self, i, v):
        """Same as `setValues()`"""
        if isinstance(i, slice):
            dtype  = _petsc.PetscInt
            vsize  = _petsc.VecGetSize(self)
            start, stop, stride = i.indices(vsize)
            i = _numpy.arange(start, stop, stride, dtype)
        self.setValues(i, v)

    # unary operations
    __pos__ = _vecops.__pos__
    __neg__ = _vecops.__neg__
    __abs__ = _vecops.__abs__
    # binary operations
    __add__ = _vecops.__add__
    __sub__ = _vecops.__sub__
    __mul__ = _vecops.__mul__
    __div__ = _vecops.__div__
    # inplace binary operations
    __iadd__ = _vecops.__iadd__
    __isub__ = _vecops.__isub__
    __imul__ = _vecops.__imul__
    __idiv__ = _vecops.__idiv__
    # reflected binary operations
    __radd__ = _vecops.__radd__
    __rsub__ = _vecops.__rsub__
    __rmul__ = _vecops.__rmul__
    __rdiv__ = _vecops.__rdiv__
    # true division operatios
    __truediv__  = _vecops.__truediv__ 
    __itruediv__ = _vecops.__itruediv__
    __rtruediv__ = _vecops.__rtruediv__
    
    def create(self, comm=None):
        """
        Creates an empty vector object. The local and global sizes can
        be set with `setSizes()` and the type can then be set with
        `setType()` (or perhaps `setFromOptions()`).

        :Parameters:
           - `comm`: MPI communicator to use (defaults to `COMM_WORLD`).

       :Returns:
         - the created vector.

        .. note:: If you never call `setSizes()` and `setType()` it
           will generate an error when you try to use the vector.
        """
        return _petsc.VecCreate(comm, self)

    def createSeq(self, size, bsize=None, comm=None):
        """
        Creates and returns a sequential vector.

        :Parameters:
           - `size`:  vector length.
           - `bsize`: vector block size (optional).
           - `comm`: MPI communicator to use (defaults to `COMM_SELF`,
             must be uniprocessor).

       :Returns:
         - the created sequential vector.
        """
        comm, n = _petsc.vecseq_size(comm, size, bsize)
        _petsc.VecCreateSeq(comm, n, self)
        if bsize is not None:
            _petsc.VecSetBlockSize(self, bsize)
        return self

    def createMPI(self, size, bsize=None, comm=None):
        """
        Creates and returns a parallel vector.

        :Parameters:
          - `size`: sequence ``(n, N)`` with local and global vector
            length (any can be `DECIDE` to have calculated if other
            is given) or integer indicating global size.
          - `bsize`: vector block size (optional).
          - `comm`:  MPI communicator (defaults to `COMM_WORLD`).

        :Returns:
          - the created parallel vector.
        """
        comm, n, N = _petsc.vecmpi_size(comm, size, bsize)
        _petsc.VecCreateMPI(comm, n, N, self)
        if bsize is not None:
            _petsc.VecSetBlockSize(self, bsize)
        return self

    def createShared(self, size, bsize=None, comm=None):
        """
        Creates and returns a parallel vector that uses shared memory.

        :Parameters:
          - `size`: sequence ``(n, N)`` with local and global vector
            length (any can be `DECIDE` to have calculated if other
            is given) or integer indicating global size.
          - `bsize`: vector block size (optional).
          - `comm`:  MPI communicator (defaults to `COMM_WORLD`).

       .. note:: Currently `VecShared` is available only on the SGI.
          Otherwise, this `Vec` is the same as `VecMPI`.

        :Returns:
          - the created shared vector.
          """
        comm, n, N = _petsc.vecmpi_size(comm, size, bsize)
        _petsc.VecCreateShared(comm, n, N, self)
        if bsize is not None:
            _petsc.VecSetBlockSize(self, bsize)
        return self

    def createGhost(self, size, ghosts, bsize=None, comm=None):
        """
        Creates a parallel vector with ghost padding on each
        processor.

        :Parameters:
          - `size`: sequence ``(n, N)`` with local and global vector
            length (any can be `DECIDE` to have calculated if other is
            given) or integer indicating global size.
          - `ghost`: ghost nodes.
          - `bsize`: vector block size (optional).
          - `comm`:  MPI communicator (defaults to `COMM_WORLD`).

        :Returns:
          - the created gosthed vector.

        .. note:: `Vec.createGhost()` constructs the global vector
           representation (without ghost points as part of vector).
           To obtain de local vector representation, call
           `Vec.getLocalForm()`.

        .. hint:: 

           If ``vg`` is a vector instance with ghost values, use the
           following to update the ghost regions with correct values
           from the owning process::

              vg.ghostUpdate(InsertMode.INSERT,ScatterMode.FORWARD)

           Use the following to accumulate the ghost region values
           onto the owning processors::

              vg.ghostUpdate(InsertMode.ADD,ScatterMode.REVERSE)

           To accumulate the ghost region values onto the owning
           processors and then update the ghost regions correctly,
           call the later followed by the former, i.e.::

              vg.ghostUpdate(InsertMode.ADD,ScatterMode.REVERSE)
              vg.ghostUpdate(InsertMode.INSERT,ScatterMode.FORWARD)

           To overlap communication with computation in updates of
           ghost regions, call::

              vg.ghostUpdateBegin(...)
              ...
              vg.ghostUpdateBegin(...)
        """
        comm, n, N = _petsc.vecmpi_size(comm, size, bsize)
        if bsize is None:
            create = _petsc.VecCreateGhost
            args   = (comm, n, N, ghosts, self)
        else:
            create = _petsc.VecCreateGhostBlock
            args   = (comm, bsize, n, N, ghosts, self)
        return create(*args)
        
    def getSize(self):
        """
        Returns the global number of elements of the vector.
        """
        return _petsc.VecGetSize(self)

    def getLocalSize(self):
        """
        Returns the local number of elements of the vector.
        """
        return _petsc.VecGetLocalSize(self)

    def getSizes(self):
        """
        Returns the local and global sizes of a vector.
        """
        lsize = _petsc.VecGetLocalSize(self)
        gsize = _petsc.VecGetSize(self)
        return (lsize, gsize)

    def setSizes(self, sizes, bsize=None):
        """
        Sets the local and global sizes of a vector.
        """
        comm = _petsc.PetscObjectGetComm(self)
        if _petsc.PetscCommGetSize(comm) == 1:
            comm, n = _petsc.vecseq_size(comm, sizes, bsize)
            N = n
        else:
            comm, n, N = _petsc.vecmpi_size(comm, sizes, bsize)
        _petsc.VecSetSizes(self, n, N)
        if bsize is not None:
            _petsc.VecSetBlockSize(self, bsize)
        
    def getBlockSize(self):
        """
        Gets the blocksize for the vector, i.e. what is used for
        `setValuesBlocked()` and `setValuesBlockedLocal()`.

        .. note:: All vectors obtained by `duplicate()` inherit the
           same block size.
        """
        return _petsc.VecGetBlockSize(self)

    def setBlockSize(self, bsize):
        """
        Sets the blocksize for future calls to `setValuesBlocked()`
        and `setValuesBlockedLocal()`.

        .. note:: All vectors obtained by `duplicate()` inherit the
           same block size.
        """
        bsize = _petsc.obj_bsize(bsize)
        _petsc.VecSetBlockSize(self, bsize)

    def getOwnershipRange(self):
        """
        Returns the range of indices owned by this processor, assuming
        that the vectors are laid out with the first *n1* elements on
        the first processor, next *n2* elements on the second, etc.
        For certain parallel layouts this range may not be well
        defined.
        """
        return tuple(_petsc.VecGetOwnershipRange(self))

    def duplicate(self):
        """
        Creates and returns qa new vector of the same type structure
        (parallel layout) as an existing vector.

        .. tip:: Use `duplicate()` to form additional vectors of the
           same type and parallel layout as an existing vector.
        """
        return _petsc.VecDuplicate(self)

    def copy(self, vec=None):
        """
        Copies a vector.

        :Parameters:
          - `vec` : vector where to copy values (optional)

        :Returns:
           - None if `vec` is provided. Otherwise, a new vector is
             created with `duplicate()`, values are copied to it, and
             that vector is returned.
        
        .. note:: For default parallel PETSc vectors, both `self` and
           `vec` must be distributed in the same manner; local copies
           are done.
        """
        if vec is None:
            vec = _petsc.VecDuplicate(self)
        _petsc.VecCopy(self, vec)
        return vec

    @staticmethod
    def Load(viewer, vec_type=None):
        """
        Loads and returns a vector that has been stored in binary
        format with `view()`.
        """
        vec_type = _petsc.get_attr(Vec.Type, vec_type)
        return _petsc.VecLoad(viewer, vec_type)

    def loadIntoVector(self, viewer):
        """
        Loads a vector that has been stored in binary format
        with `view()`.
        """
        _petsc.VecLoadIntoVector(viewer, self)

    def setOption(self, option):
        """
        Sets an option for controling a vector's behavior.
        """
        try:
            options = iter(option)
        except TypeError:
            options = (option,)
        for option in options:
            opt = _petsc.get_attr(Vec.Option, option)
            _petsc.VecSetOption(self, opt)

    def equal(self, vec):
        """
        Compares two vectors.
        """
        return bool(_petsc.VecEqual(self, vec))

    def dot(self, vec):
        """
        Computes the vector dot product.
        """
        return _petsc.VecDot(self, vec)
    
    def dotBegin(self, vec):
        """
        Starts a split phase dot product computation.
        """
        _petsc.VecDotBegin(self, vec)

    def dotEnd(self, vec):
        """
        Ends a split phase dot product computation.
        """
        return _petsc.VecDotEnd(self, vec)

    def tDot(self, vec):
        """
        Computes an indefinite vector dot product. That is, this
        routine does NOT use the complex conjugate.
        """
        return _petsc.VecTDot(self, vec)
                              
    def tDotBegin(self, vec):
        """
        """
        _petsc.VecTDotBegin(self, vec)

    def tDotEnd(self, vec):
        """
        """
        return _petsc.VecTDotEnd(self, vec)

    def norm(self, norm_type=None):
        """
        Computes the vector norm.
        """
        return _petsc.VecNorm(self, norm_type)
    
    def normBegin(self, norm_type=None):
        """
        """
        _petsc.VecNormBegin(self, norm_type)

    def normEnd(self, norm_type=None):
        """
        """
        return _petsc.VecNormEnd(self, norm_type)
    
    def sum(self):
        """
        Computes the sum of all the components of a vector.
        """
        return _petsc.VecSum(self)
                             
    def min(self):
        """
        Determines the minimum vector component and its location.
        """
        return tuple(_petsc.VecMin(self))

    def max(self):
        """
        Determines the maximum vector component and its location.
        """
        return tuple(_petsc.VecMax(self))
                             
    def normalize(self):
        """
        Normalizes a vector by 2-norm and returns original 2-norm.
        """
        return _petsc.VecNormalize(self)

    def reciprocal(self):
        """self[i] <- 1 / self[i]"""
        _petsc.VecReciprocal(self)
    
    def sqrt(self):
        """self[i] <- sqrt | self[i] |"""
        _petsc.VecSqrt(self)

    def abs(self):
        """self[i] <- abs self[i]"""
        _petsc.VecAbs(self)

    def conjugate(self):
        """self[i] <- conj self[i]"""
        _petsc.VecConjugate(self)
        
    def setRandom(self, random=None):
        """self[i] <- random()"""
        _petsc.VecSetRandom(self, random)

    def zeroEntries(self):
        """self[i] <- 0"""
        _petsc.VecZeroEntries(self)

    def set(self, alpha):
        """self[i] <- alpha"""
        _petsc.VecSet(self, alpha)
    
    def scale(self, alpha):
        """self[i] <- alpha * self[i]"""
        _petsc.VecScale(self, alpha)
                               
    def shift(self, alpha):
        """self[i] <- self[i] + alpha"""
        _petsc.VecShift(self, alpha)
    
    def swap(self, vec):
        """self <-> vec"""
        _petsc.VecSwap(self, vec)

    def axpy(self, alpha, vec):
        """self <- alpha * vec + self"""
        _petsc.VecAXPY(self, alpha, vec)

    def aypx(self, alpha, vec):
        """self <- alpha * self + vec"""
        _petsc.VecAYPX(self, alpha, vec)
    
    def axpby(self, alpha, beta, vec):
        """self <- alpha * vec + beta * self"""
        _petsc.VecAXPBY(self, alpha, beta, vec)

    def waxpy(self, alpha, vec1, vec2):
        """self <- alpha * vec1 + vec2"""
        _petsc.VecWAXPY(self, alpha, vec1, vec2)

    AXPY  = axpy
    AYPX  = aypx
    AXPBY = axpby
    WAXPY = waxpy    

    def pointwiseMult(self, vec1, vec2):
        """self[i] <- vec1[i] * vec2[i]"""
        _petsc.VecPointwiseMult(self, vec1, vec2)

    def pointwiseDivide(self, vec1, vec2):
        """self[i] <- vec1[i] / vec2[i]"""
        _petsc.VecPointwiseDivide(self, vec1, vec2)

    def pointwiseMax(self, vec1, vec2):
        """self[i] <- max (vec1[i], vec2[i])"""
        _petsc.VecPointwiseMax(self, vec1, vec2)

    def pointwiseMin(self, vec1, vec2):
        """self[i] <- min(vec1[i], vec2[i])"""
        _petsc.VecPointwiseMin(self, vec1, vec2)

    def pointwiseMaxAbs(self, vec1, vec2):
        """self[i] <- max(abs(vec1[i]), abs(vec2[i]))"""
        _petsc.VecPointwiseMax(self, vec1, vec2)

    def maxPointwiseDivide(self, vec):
        """max abs(self[i]/vec[i])"""
        _petsc.VecMaxPointwiseDivide(self, vec)

    def permute(self, order, invert=False):
        """
        Permutes a vector in place using the given ordering

        :Parameters:
          - `order`: index set with permutation
          - `invert`: boolean for inverting the permutation
        """
        _petsc.VecPermute(self, order, invert)
                                 
    def getArray(self, array=None):
        """
        Returns an array that contains this processor's portion of the
        vector data. This method makes a copy.
        """
        if array is None:
            vsize  = _petsc.VecGetLocalSize(self)
            array = _numpy.empty(vsize, _petsc.PetscScalar)
        _petsc.VecGetArray(self, array)
        return array

    def setArray(self, array):
        """
        Sets this processor's portion of the vector data.
        """
        _petsc.VecSetArray(self, array)

    def placeArray(self, array):
        """
        Allows to replace the array in a vector with an array provided
        by the user. This is useful to avoid copying an array into a
        vector.

        :Parameters:
          - `array` - the array.

        ..notes:: You can return to the original vector array with a
          call to `resetArray()`.
        """
        _petsc.VecPlaceArray(self, array)

    def resetArray(self):
        """
        Resets a vector to use its default memory. Call this 
        after the use of `placeArray()`.
        """
        _petsc.VecResetArray(self)

    def getValue(self, index):
        """
        Gets a single entry from a vector.
        """
        return _petsc.VecGetValue(self, index)

    def getValues(self, indices, values=None):
        """
        Gets a block of values from a vector.
        """
        if values is None:
            indices = _numpy.asarray(indices, _petsc.PetscInt)
            vshape = _numpy.shape(indices)
            values = _numpy.empty(vshape, _petsc.PetscScalar)
        _petsc.VecGetValues(self, indices, values)
        return values

    def setValue(self, index, value, insert_mode=None):
        """
        Sets a single value.
        """
        _petsc.VecSetValue(self, index, value, insert_mode)

    def setValues(self, indices, values, insert_mode=None):
        """
        Inserts or adds values into certain locations of a vector.

        :Parameters:
          - `indices`: array of indices.
          - `values`: array of values.
          - `insert_mode`: either `INSERT_VALUES` to replaces existing
            entries with new values, or `ADD_VALUES` to add values to
            any existing entries.
        """
        _petsc.VecSetValues(self, indices, values, insert_mode)
        
    def setLGMapping(self, lgmap):
        """
        Sets a local numbering to global numbering used by
        `setValuesLocal()` to allow users to insert vector entries
        using a local (per-processor) numbering.
        """
        _petsc.VecSetLocalToGlobalMapping(self, lgmap)

    def setValueLocal(self, index, value, insert_mode=None):
        """
        """
        _petsc.VecSetValueLocal(self, index, value, insert_mode)

    def setValuesLocal(self, indices, values, insert_mode=None):
        """
        """
        _petsc.VecSetValuesLocal(self, indices, values, insert_mode)

    def setValuesBlocked(self, indices, values, insert_mode=None):
        """
        """
        _petsc.VecSetValuesBlocked(self, indices, values, insert_mode)
        
    def setLGMappingBlock(self, lgmap):
        """
        """
        _petsc.VecSetLocalToGlobalMappingBlock(self, lgmap)

    def setValuesBlockedLocal(self, indices, values,
                              insert_mode=None):
        """
        """
        _petsc.VecSetValuesBlockedLocal(self, indices, values,
                                        insert_mode)

    def assemblyBegin(self):
        """
        Begins assembling the vector.  This routine should be called
        after completing all calls to `setValues()`.
        """
        _petsc.VecAssemblyBegin(self)

    def assemblyEnd(self):
        """
        Completes assembling the vector.  This routine should be
        called after `assemblyBegin()`.
        """
        _petsc.VecAssemblyEnd(self)

    def assemble(self):
        """
        Calls `assemblyBegin()` and `assemblyEnd()`.
        """
        _petsc.VecAssemblyBegin(self)
        _petsc.VecAssemblyEnd(self)

    # methods for strided vectors

    def strideScale(self, field, alpha):
        """
        """
        _petsc.VecStrideScale(self, field, alpha)
        
    def strideMax(self, field):
        """
        """
        return tuple(_petsc.VecStrideMax(self, field))

    def strideMin(self, field):
        """
        """
        return tuple(_petsc.VecStrideMin(self, field))
        
    def strideNorm(self, field, norm_type=None):
        """
        """
        return _petsc.VecStrideNorm(self, field, norm_type)

    def strideScatter(self, field, vec, insert_mode=None):
        """
        """
        _petsc.VecStrideScatter(self, field, vec, insert_mode)
        
    def strideGather(self, field, vec, insert_mode=None):
        """
        """
        _petsc.VecStrideGather(self, field, vec, insert_mode)

    # methods for vectors with ghost values

    def getLocalForm(self):
        """
        Obtains the local ghosted representation of a parallel
        vector.

        .. note:: This routine does not actually update the ghost
           values, but rather it returns a sequential vector that
           includes the locations for the ghost values and their
           current values. The returned vector and the original vector
           passed in share the same array that contains the actual
           vector data.
        """
        return _petsc.VecGhostGetLocalForm(self)

    def ghostUpdateBegin(self, insert_mode, scatter_mode):
        """
        Begins the vector scatter to update the vector from local
        representation to global or global representation to local.
        """
        _petsc.VecGhostUpdateBegin(self, insert_mode, scatter_mode)

    def ghostUpdateEnd(self, insert_mode, scatter_mode):
        """
        Ends the vector scatter to update the vector from local
        representation to global or global representation to local.
        """
        _petsc.VecGhostUpdateEnd(self, insert_mode, scatter_mode)

    def ghostUpdate(self, insert_mode, scatter_mode):
        """
        Updates the vector from local representation to global or
        global representation to local.
        """
        _petsc.VecGhostUpdateBegin(self, insert_mode, scatter_mode)
        _petsc.VecGhostUpdateEnd(self, insert_mode, scatter_mode)

    option = property(fset=setOption,
                      doc='Set an option or sequence of options')
    array = property(getArray, setArray)
    sizes = property(getSizes, setSizes)
    
    size  = property(getSize)
    lsize = local_size  = property(getLocalSize)
    gsize = global_size = property(getSize)
    bsize = block_size  = property(getBlockSize, setBlockSize)
    range = owner_range = property(getOwnershipRange)

    # Array Interface V3, Python side
    __array_interface__ = property(_petsc.Vec__array_interface__,
                                   doc='Array protocol: interface')

# --------------------------------------------------------------------

class VecSeq(Vec):
    """
    Sequential vector implementation.
    """
    __metaclass__ = Vec.Type(Vec.Type.SEQ)
    def __init__(self, *targs, **kwargs):
        super(VecSeq, self).__init__(*targs, **kwargs)
        self.createSeq(*targs, **kwargs)
        
class VecMPI(Vec):
    """
    Parallel vector implementation.
    """
    __metaclass__ = Vec.Type(Vec.Type.MPI)
    def __init__(self, *targs, **kwargs):
        super(VecMPI, self).__init__(*targs, **kwargs)
        self.createMPI(*targs, **kwargs)

class VecShared(Vec):
    """
    Parallel vector implementation that uses shared memory.
    """
    __metaclass__ = Vec.Type(Vec.Type.SHARED)
    def __init__(self, *targs, **kwargs):
        super(VecShared, self).__init__(*targs, **kwargs)
        self.createShared(*targs, **kwargs)

class VecSieve(Vec):
    """
    The parallel vector implementation based upon Sieve fields.
    """
    __metaclass__ = Vec.Type(Vec.Type.SIEVE)
    def __init__(self, *targs, **kwargs):
        super(VecSieve, self).__init__(*targs, **kwargs)
        #self.createSieve(*targs, **kwargs)
        raise NotImplementedError

# --------------------------------------------------------------------


class Scatter(Object):

    """
    Object used to manage communication of data between vectors in
    parallel. Manages both scatters and gathers::

       y[iy[i]] = x[ix[i]], for i=0,...,ni-1

    This scatter is far more general than the conventional MPI
    scatter, since it can be a gather or a scatter or a combination,
    depending on the indices ``ix`` and ``iy``.  If ``x`` is a
    parallel vector and ``y`` is sequential, `Scatter()` can serve to
    gather values to a single processor.  Similarly, if ``y`` is
    parallel and ``x`` sequential, the routine can scatter from one
    processor to many processors.

    .. note:: 

       In calls to `Scatter.[begin|end]()` you can use different
       vectors than the `vec_from` and `vec_to` you used to create the
       scatter context; BUT they must have the same parallel data
       layout, for example, they could be obtained from
       `Vec.duplicate()`.

       A scatter context **CANNOT** be used in two or more
       simultaneous scatters; that is you cannot call a second
       `begin()` with the same scatter context until a matching
       `end()` has been called. In this case a separate scatter
       context is needed for each concurrent scatter, for example it
       could be obtained with `copy()`.

       You cannot change the values in the input vector between the
       calls to `begin()` and `end()`.

       If you use `ScatterMode.REVERSE` the first two arguments for
       `begin()` and `end()` should be reversed, from the
       `ScatterMode.FORWARD`.
    """

    def __init__(self, *targs, **kwargs):
        """See `create()`"""
        super(Scatter, self).__init__(*targs, **kwargs)
        if targs or kwargs:
            self.create(*targs, **kwargs)
        
        
    def __call__(self, vec_from, vec_to, insert_mode, scatter_mode):
        """Same as `scatter()`"""
        self.scatter(vec_from, vec_to, insert_mode, scatter_mode)

    def create(self, vec_from, is_from, vec_to, is_to):
        """
        Creates a vector scatter context.

        :Parameters:
          - `vec_from`: a vector that defines the shape (parallel data
            layout of the vector) of vectors from which we scatter.
          - `is_from`: the indices of `vec_from` to scatter (or
            ``None`` to scatter all values).
          - `vec_to`: a vector that defines the shape (parallel data
            layout of the vector) of vectors to which we scatter.
          - `is_to`: the indices of `vec_to` to hold results (or
            ``None`` to fill all values).
        """
        _petsc.VecScatterCreate(vec_from, is_from,
                                vec_to,   is_to, self)
    
    def copy(self):
        """
        Makes a copy of a scatter context.
        """
        return _petsc.VecScatterCopy(self)
    
    @staticmethod
    def toAll(vec):
        """
        Creates a scatter context that copies all vector values to
        each processor.

        :Parameters: 
          - `vec`: input `VecMPI` instance.

        :Returns:
          - `Scatter` context.
          - `VecSeq` that is large enough to scatter into.

        .. tip::
          # create scatter context and local vector
          scatter, vout = Scatter.toAll(vin)
          # scatter as many times as you need
          ins_mode = InsertMode.INSERT
          sct_mode = ScatterMode.FORWARD
          scatter.begin(vin, vout, ins_mode, sct_mode)
          scatter.end(vin, vout,ins_mode, sct_mode)
          # destroy scatter and vector when no longer needed
          scatter.destroy()
          vout.destroy()
        """
        return tuple(_petsc.VecScatterCreateToAll(vec))

    @staticmethod
    def toZero(vec):
        """
        Creates a scatter context that copies all vector values to a
        vector on the zeroth processor

        :Returns:
          - `Scatter` context.
          - `VecSeq` that is large enough to scatter into on
            processor 0 and of length zero on all other processors

        .. tip::
          # create scatter context and local vector
          scatter, vout = Scatter.toZero(vin)
          # scatter as many times as you need
          ins_mode = InsertMode.INSERT
          sct_mode = ScatterMode.FORWARD
          scatter.begin(vin, vout, ins_mode, sct_mode)
          scatter.end(vin, vout,ins_mode, sct_mode)
          # destroy scatter and vector when no longer needed
          scatter.destroy()
          vout.destroy()
        """
        return tuple(_petsc.VecScatterCreateToZero(vec))

    def begin(self, vec_from, vec_to, insert_mode, scatter_mode):
        """
        Begins a generalized scatter from one vector to
        another. Complete the scattering phase with `scatterEnd()`.
        """
        _petsc.VecScatterBegin(vec_from, vec_to,
                               insert_mode, scatter_mode, self)

    def end(self, vec_from, vec_to, insert_mode, scatter_mode):
        """
        Ends a generalized scatter from one vector to another.
        Call after first calling `scatterBegin()`.
        """
        _petsc.VecScatterEnd(vec_from, vec_to,
                             insert_mode, scatter_mode, self)

    scatterBegin = begin

    scatterEnd   = end

    def scatter(self, vec_from, vec_to,
                insert_mode, scatter_mode):
        """
        Generalized scatter from one vector to another.
        """
        _petsc.VecScatterBegin(vec_from, vec_to,
                               insert_mode, scatter_mode, self)
        _petsc.VecScatterEnd(vec_from, vec_to,
                             insert_mode, scatter_mode, self)
    

# --------------------------------------------------------------------
