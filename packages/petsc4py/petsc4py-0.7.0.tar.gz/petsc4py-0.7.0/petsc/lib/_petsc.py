# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

# Try to import default PETSc extension
# module if it was not previously done;
# if it was, this is a no-op.
import petsc4py.lib
_petsc = petsc4py.lib.Import()

# Import PETSc extension module
from petsc4py.lib._petscext import *
from petsc4py.lib import _numpy

# Try to initialize PETSc
if not _petsc.PetscInitialized():
    if not _petsc.PetscFinalized():
        _petsc.PetscInitialize()

# Helper function to get attributes form object
# instances and classes using strings.
def get_attr(obj, attr, default=None):
    if attr is None:
        return default
    elif type(attr) is str:
        return getattr(obj, attr.replace('-','_').upper())
    else:
        return attr

# Helper functions to replace a communicator handle
def PetscCommSetComm(self, comm):
    _petsc.PetscCommSetComm(self, comm)
    
# Helper function to get a type.
def get_type(obj, otype):
    if type(otype) is str:
        types = getattr(obj, 'Type', None)
        if types is not None:
            attr = otype.replace('-','_').upper()
            otype = getattr(types, attr, otype)
    return otype

# Helper functions to check block sizes
def obj_bsize(bsz, default=None):
    if default is not None:
        if bsz is None:
            bsz = default
    if not isinstance(bsz, int):
        tpname = type(bsz).__name__
        errmess = "block size must be integer, not '%s'" % tpname
        raise TypeError(errmess)
    elif bsz <= 0:
        errmess = 'block size must be positive, not %d' % bsz
        raise ValueError(errmess)
    return bsz


# Helper function to parse and check size arguments
# for sequential vectors
def vecseq_size(comm, size, bsize=None):
    # communicator
    if comm is None:
        comm = _petsc.PetscGetCommSelf()
    else:
        if _petsc.PetscCommGetSize(comm) != 1:
            raise ValueError('not a sequential communicator')
    DECIDE = _petsc.PETSC_DECIDE
    # size
    if size is None:
        raise ValueError("size cannot be None")
    elif size == DECIDE:
        raise ValueError("size cannot be 'DECIDE'")
    elif not isinstance(size, int):
        try:
            lsize, gsize = size
        except ValueError:
            raise ValueError("size must be integer or sequence with two items")
        except TypeError:
            raise TypeError("size must be integer or sequence with two items")
        if lsize == gsize:
            size = gsize
        elif gsize is None or gsize == DECIDE:
            size = lsize
        elif lsize is None or lsize == DECIDE:
            size = gsize
        else:
            raise ValueError('local size must equal global size')
        if size is None:
            raise ValueError("size cannot be None")
        elif size == DECIDE:
            raise ValueError("size cannot be 'DECIDE'")
        elif not isinstance(size, int):
            raise TypeError("size must be integer")
    if size < 0:
        raise ValueError("size must be a nonnegative integer")
    # block size
    if bsize is not None:
        if not isinstance(bsize, int):
            raise TypeError('block size must be integer')
        elif bsize <= 0:
            raise ValueError('block size must be positive')
        elif size % bsize != 0:
            raise ValueError('size %d must be divisible by block size %d' % (size, bsize))
    return comm, size


# Helper function to parse and check size arguments
# for distributed vectors
def vecmpi_size(comm, size, bsize=None):
    # communicator
    if comm is None:
        comm = _petsc.PetscGetCommWorld()
    # get local size and global size
    DECIDE = _petsc.PETSC_DECIDE
    if size is None:
        raise ValueError('size cannot be None')
    elif size == DECIDE:
        raise ValueError("size cannot be 'DECIDE'")
    elif isinstance(size, int):
        lsize, gsize = DECIDE, size
    else:
        try:
            lsize, gsize = size
        except ValueError:
            raise ValueError('size must be integer or sequence with two items')
        except TypeError:
            raise TypeError('size must be integer or sequence with two items')
    # local size
    if lsize is None:
        lsize = DECIDE
    elif lsize != DECIDE:
        if not isinstance(lsize, int):
            raise TypeError('local size must be integer')
        elif lsize < 0:
            raise ValueError('local size must be nonnegative')
    # global size
    if gsize is None:
        gsize = DECIDE
    elif gsize != DECIDE:
        if not isinstance(gsize, int):
            raise TypeError('global size must be integer')
        elif gsize < 0:
            raise ValueError('global size must be nonnegative')
    # check local and global sizes
    if lsize == DECIDE and gsize == DECIDE:
        raise ValueError("local and global sizes cannot be both 'DECIDE'")
    # block size compatibility
    if bsize is None:
        lsize, gsize = _petsc.PetscSplitOwnership(comm, lsize, gsize)
    else:
        if not isinstance(bsize, int):
            raise TypeError('block size must be integer')
        elif bsize <= 0:
            raise ValueError('block size must be positive')
        lsize, gsize = _petsc.PetscSplitOwnershipBlock(comm, bsize,
                                                       lsize, gsize)
    return comm, lsize, gsize


# Helper function to parse and check size
# arguments for sequential matrices
def matseq_sizes(comm, size, bsize=None):
    # communicator
    if comm is None:
        comm = _petsc.PetscGetCommSelf()
    else:
        if _petsc.PetscCommGetSize(comm) != 1:
            raise ValueError('not a sequential communicator')
    DECIDE = _petsc.PETSC_DECIDE
    # row and column size
    if size is None:
        raise ValueError('size cannot be None')
    elif size == DECIDE:
        raise ValueError("row and column size cannot be 'DECIDE'")
    elif isinstance(size, int):
        if size < 0:
            raise ValueError('row and column size must be nonnegative')
        m = n = size
    else:
        try:
            m, n = size
        except TypeError:
            raise TypeError('size must be integer or sequence with two integer items')
        except ValueError:
            raise ValueError('size must be integer or sequence with two integer items')
        # row size
        if m is None:
            raise ValueError('row size cannot be None')
        elif m == DECIDE:
            raise ValueError("row size cannot be 'DECIDE'")
        elif not isinstance(m, int):
            raise TypeError('row size must be integer')
        elif m < 0:
            raise ValueError('row size must be nonnegative')
        # column size
        if n == None:
            raise ValueError('column size cannot be None')
        elif n == DECIDE:
            raise ValueError("column size cannot be 'DECIDE'")
        elif not isinstance(n, int):
            raise TypeError('column size must be integer')
        elif n < 0:
            raise ValueError('column size must be nonnegative')
    # block size compatibility
    if bsize is not None:
        if not isinstance(bsize, int):
            raise TypeError('block size must be integer')
        elif bsize <= 0:
            raise ValueError('block size must be positive')
        if m % bsize != 0:
            raise ValueError('row size %d must be divisible by block size %d' % (m, bsize))
        elif n % bsize != 0:
            raise ValueError('column size %d must be divisible by block size %d' % (n, bsize))
    # return data
    return comm, m, n


# Helper function to parse and check size
# arguments for distributed matrices
def matmpi_sizes(comm, size, bsize=None):
    if comm is None:
        comm = _petsc.PetscGetCommWorld()
    DECIDE = _petsc.PETSC_DECIDE
    # size
    if size is None:
        raise ValueError('size cannot be None')
    elif size == DECIDE:
        raise ValueError("size cannot be 'DECIDE'")
    elif isinstance(size, int):
        lsize, gsize = DECIDE, size
    else:
        try:
            lsize, gsize = size
        except ValueError:
            raise ValueError('size must be integer or sequence with two items')
        except TypeError:
            raise TypeError('size must be integer or sequence with two items')
    # local size
    if lsize is None or lsize == DECIDE:
        m = n = DECIDE
    else:
        if isinstance(lsize, int):
            m = n = lsize
        else:
            try:
                m, n = lsize
            except TypeError:
                raise TypeError('local size must be integer or sequence with two integer items')
            except ValueError:
                raise ValueError('local size must be integer or sequence with two integer items')
        # local row size
        if m is None:
            m = DECIDE
        elif m != DECIDE:
            if not isinstance(m, int):
                raise TypeError('local row size must be integer')
            elif m < 0:
                raise ValueError('local row size must be nonnegative')
        # local column size
        if n is None:
            n = DECIDE
        elif n != DECIDE:
            if not isinstance(n, int):
                raise TypeError('local column size must be integer')
            elif n < 0:
                raise ValueError('local column size must be nonnegative')
    # global size
    if gsize is None or gsize == DECIDE:
        M = N = DECIDE
    else:
        if isinstance(gsize, int):
            M = N = gsize
        else:
            try:
                M, N = gsize
            except TypeError:
                raise TypeError('global size must be integer or sequence with two integer items')
            except ValueError:
                raise ValueError('global size must be integer or sequence with two integer items')
        # global row size
        if M is None:
            M = DECIDE
        elif M != DECIDE:
            if not isinstance(M, int):
                raise TypeError('global row size must be integer')
            elif M < 0:
                raise ValueError('global row size must be nonnegative')
        # global column size
        if N is None:
            N = DECIDE
        elif N != DECIDE:
            if not isinstance(N, int):
                raise TypeError('global column size must be integer')
            elif N < 0:
                raise ValueError('global column size must be nonnegative')
    # check local and global sizes
    if m == DECIDE and M == DECIDE:
        raise ValueError("local and global row sizes cannot be both 'DECIDE'")
    if n == DECIDE and N == DECIDE:
        raise ValueError("local and global column sizes cannot be both 'DECIDE'")
    # block size compatibility
    if bsize is None:
        m, M = _petsc.PetscSplitOwnership(comm, m, M)
        n, N = _petsc.PetscSplitOwnership(comm, n, N)
    else:
        if not isinstance(bsize, int):
            raise TypeError('block size must be integer')
        elif bsize <= 0:
            raise ValueError('block size must be positive')
        m, M = _petsc.PetscSplitOwnershipBlock(comm, bsize, m, M)
        n, N = _petsc.PetscSplitOwnershipBlock(comm, bsize, n, N)
    return comm, m, n, M, N
    

# Helper function to parse and check
# non-zero preallocation data for AIJ matrices
def mataij_nz(nrows, nz, bs=None):
    DECIDE = _petsc.PETSC_DECIDE
    if nz is None:
        return DECIDE, None
    elif isinstance(nz, int):
        if nz != DECIDE and nz < 0:
            raise ValueError('number of non-zeros must be nonnegative')
        return nz, None
    else:
        nz = _numpy.asarray(nz, _petsc.PetscInt)
        if bs is None:
            if nrows != _numpy.size(nz):
                raise ValueError('incompatible non-zeros array length and row size')
        else:
            if nrows != _numpy.size(nz) * bs:
                raise ValueError('incompatible non-zeros array length and block row size')
        return DECIDE, nz


# Helper function to parse and check
# CSR preallocation data for AIJ matrices
def mataij_csr(nrows, csr, bs=None):
    try:
        csr = tuple(csr)
        if len(csr) == 2:
            csr = csr + (None,)
        elif len(csr) != 3:
            raise ValueError
    except TypeError:
        raise TypeError('CSR data must be a sequence with two or three array items')
    except ValueError:
        raise ValueError('CSR data must be a sequence with two or three array items')
    i, j, v = csr
    bs = bs or 1
    i = _numpy.asarray(i, _petsc.PetscInt)
    if i[0] != 0:
        raise ValueError('invalid CSR data, I[0] != 0')
    if nrows != (_numpy.size(i) - 1) * bs:
        raise ValueError('invalid CSR data, rows != (size(I) - 1) * bs')
    j = _numpy.asarray(j, _petsc.PetscInt)
    if _numpy.size(j) != i[-1]:
        raise ValueError('invalid CSR data, size(J) != I[-1]')
    if v is not None:
        v = _numpy.asarray(v, _petsc.PetscScalar)
        if _numpy.size(v) != _numpy.size(j) * (bs**2):
            raise ValueError('invalid CSR data, size(V) != size(J) * bs^2')
    return i, j, v


# Helper function to dispatch matrix preallocation
# routines, mainly for AIJ matrix variants
def MatSetPreallocation(A, nz=None, csr=None):
    
    mat_type = _petsc.MatGetType(A)

    is_seq = 'seq'   in mat_type
    is_mpi = 'mpi'   in mat_type
    is_aij = 'aij'   in mat_type
    is_blk = 'baij'  in mat_type
    is_sym = 'sbaij' in mat_type

    if not is_seq and not is_mpi:
        comm = _petsc.PetscObjectGetComm(A)
        size = _petsc.PetscCommGetSize(comm)
        if size == 1:
            is_seq = True
        else:
            is_mpi = True

    if is_seq:
        frag = 'Seq'
    if is_mpi:
        frag = 'MPI'
    if is_sym:
        frag += 'S'
    if is_blk:
        frag += 'B'

    if is_aij:
        frag = 'Mat%sAIJSetPreallocation' % frag
        if is_blk:
            bs = _petsc.MatGetBlockSize(A)
            preallocdata = (A, bs)
        else:
            bs = None
            preallocdata = (A,)
        m, _ = _petsc.MatGetLocalSize(A)
        if csr is None:
            if type(nz) in (tuple, list) and len(nz) == 2:
                d_nz, o_nz = nz
            else:
                d_nz, o_nz = nz, None
            if is_seq:
                preallocdata += mataij_nz(m, d_nz, bs)
            else:
                preallocdata += mataij_nz(m, d_nz, bs)
                preallocdata += mataij_nz(m, o_nz, bs)
        else:
            frag += 'CSR'
            preallocdata += mataij_csr(m, csr, bs)
        try:
            preallocfunc = getattr(_petsc, frag)
        except AttributeError:
            raise TypeError('no support for preallocating '
                            'this matrix type: %s' % mat_type)
    elif mat_type == _petsc.MATIS:
        preallocfunc = MatSetPreallocation
        preallocdata = (_petsc.MatISGetLocalMat(A),) + (nz, csr)
    else:
        preallocfunc = lambda *args: None
        preallocdata = ()

    preallocfunc(*preallocdata)



# Helper class to manage MatFactorInfo structure
# used in matrix factorization routines
class MatFactorInfo(object):
    
    DEFAULT = None
    
    __keymap = {'shiftnz'        :  0,
                'shiftpd'        :  1,
                'shift_fraction' :  2,
                'diagonal_fill'  :  3,
                'dt'             :  4,
                'dtcol'          :  5,
                'dtcount'        :  6,
                'fill'           :  7,
                'levels'         :  8,
                'pivotinblocks'  :  9,
                'zeropivot'      : 10 }

    def __init__(self, *targs, **kwargs):
        self.__info = _numpy.zeros(len(self), _petsc.PetscReal)
        default = getattr(self, 'DEFAULT', None)
        if default is not None:
            self.update(default)
        if targs:
            for arg in targs:
                self.update(arg)
        if kwargs:
            self.update(kwargs)

    def __len__(self):
        return len(self.__keymap)

    def __iter__(self):
        keys = self.__keymap
        info = self.__info
        for k, i in keys.iteritems():
            yield k, info[i].item()

    def __contains__(self, key):
        return key in self.__keymap

    def __getitem__(self, key):
        idx = self.__keymap.get(key)
        if idx is None:
            raise KeyError, 'invalid key: %s' % key
        return self.__info[idx].item()

    def __setitem__(self, key, value):
        idx = self.__keymap.get(key)
        if idx is None:
            raise KeyError, 'invalid key: %s' % key
        self.__info[idx] = _petsc.PetscReal(value)

    def __array__(self, dtype=None):
        if dtype is None:
            return self.__info
        else:
            return self.__info.astype(dtype)

    def update(self, obj, **kwargs):
        try:
            sequence = obj.iteritems()
        except AttributeError:
            sequence = obj
        for key, value in sequence:
            self[key] = value
        for key, value in kwargs.iteritems():
            self[key] = value


# Helper function used to define properties for
# managing tolerances in KSP and SNES instances
def tolerance(keyword, index, doc=None):
    def fget(self):
        return self.getTolerances()[index]
    def fset(self, tol):
        self.setTolerances(**{keyword : tol})
    return fget, fset, None, doc
