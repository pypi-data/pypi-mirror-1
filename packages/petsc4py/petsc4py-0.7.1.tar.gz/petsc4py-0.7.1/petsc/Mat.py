# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Matrices (Mat)
==============

A large suite of data structures and code for the manipulation of
parallel sparse matrices. Includes different parallel matrix data
structures, each appropriate for a different class of problems.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['Mat',

           'MatSeqDense',
           'MatMPIDense',

           'MatSeqAIJ',
           'MatMPIAIJ',
           'MatSeqBAIJ',
           'MatMPIBAIJ',
           'MatSeqSBAIJ',
           'MatMPISBAIJ',
           ## 'MatSeqBDiag',
           ## 'MatMPIBDiag',
           
           'MatIS',
           'MatScatter',
           'MatNormal',
           'MatShell',

           'NullSpace']

# --------------------------------------------------------------------

from petsc4py.lib import _petsc
from petsc4py.lib import _matops
from petsc4py.lib import _numpy

from petsc4py.Object import Object

# --------------------------------------------------------------------



class Mat(Object):

    """
    Abstract PESTc matrix object.
    """

    class Type:
        """
        Mat types.
        """
        SAME            = _petsc.MATSAME           
        SEQMAIJ         = _petsc.MATSEQMAIJ        
        MPIMAIJ         = _petsc.MATMPIMAIJ        
        MAIJ            = _petsc.MATMAIJ           
        IS              = _petsc.MATIS             
        MPIROWBS        = _petsc.MATMPIROWBS       
        SEQAIJ          = _petsc.MATSEQAIJ         
        MPIAIJ          = _petsc.MATMPIAIJ         
        AIJ             = _petsc.MATAIJ            
        SHELL           = _petsc.MATSHELL          
        SEQBDIAG        = _petsc.MATSEQBDIAG       
        MPIBDIAG        = _petsc.MATMPIBDIAG       
        BDIAG           = _petsc.MATBDIAG          
        SEQDENSE        = _petsc.MATSEQDENSE       
        MPIDENSE        = _petsc.MATMPIDENSE       
        DENSE           = _petsc.MATDENSE          
        SEQBAIJ         = _petsc.MATSEQBAIJ        
        MPIBAIJ         = _petsc.MATMPIBAIJ        
        BAIJ            = _petsc.MATBAIJ           
        MPIADJ          = _petsc.MATMPIADJ         
        SEQSBAIJ        = _petsc.MATSEQSBAIJ       
        MPISBAIJ        = _petsc.MATMPISBAIJ       
        SBAIJ           = _petsc.MATSBAIJ          
        DAAD            = _petsc.MATDAAD           
        MFFD            = _petsc.MATMFFD           
        NORMAL          = _petsc.MATNORMAL         
        LRC             = _petsc.MATLRC            
        SEQAIJSPOOLES   = _petsc.MATSEQAIJSPOOLES  
        MPIAIJSPOOLES   = _petsc.MATMPIAIJSPOOLES  
        SEQSBAIJSPOOLES = _petsc.MATSEQSBAIJSPOOLES
        MPISBAIJSPOOLES = _petsc.MATMPISBAIJSPOOLES
        AIJSPOOLES      = _petsc.MATAIJSPOOLES     
        SBAIJSPOOLES    = _petsc.MATSBAIJSPOOLES   
        SUPERLU         = _petsc.MATSUPERLU        
        SUPERLU_DIST    = _petsc.MATSUPERLU_DIST   
        UMFPACK         = _petsc.MATUMFPACK        
        ESSL            = _petsc.MATESSL           
        LUSOL           = _petsc.MATLUSOL          
        AIJMUMPS        = _petsc.MATAIJMUMPS       
        SBAIJMUMPS      = _petsc.MATSBAIJMUMPS     
        DSCPACK         = _petsc.MATDSCPACK        
        MATLAB          = _petsc.MATMATLAB         
        SEQCSRPERM      = _petsc.MATSEQCSRPERM     
        MPICSRPERM      = _petsc.MATMPICSRPERM     
        CSRPERM         = _petsc.MATCSRPERM        
        SEQCRL          = _petsc.MATSEQCRL         
        MPICRL          = _petsc.MATMPICRL         
        CRL             = _petsc.MATCRL            
        PLAPACK         = _petsc.MATPLAPACK
        SCATTER         = _petsc.MATSCATTER

    class Option:
        """
        Options that may be set for a matrix and its behavior or
        storage.
        """
        ROW_ORIENTED               = _petsc.MAT_ROW_ORIENTED
        COLUMN_ORIENTED            = _petsc.MAT_COLUMN_ORIENTED
        ROWS_SORTED                = _petsc.MAT_ROWS_SORTED
        COLUMNS_SORTED             = _petsc.MAT_COLUMNS_SORTED
        NO_NEW_NONZERO_LOCATIONS   = _petsc.MAT_NO_NEW_NONZERO_LOCATIONS
        YES_NEW_NONZERO_LOCATIONS  = _petsc.MAT_YES_NEW_NONZERO_LOCATIONS
        SYMMETRIC                  = _petsc.MAT_SYMMETRIC
        STRUCTURALLY_SYMMETRIC     = _petsc.MAT_STRUCTURALLY_SYMMETRIC
        NO_NEW_DIAGONALS           = _petsc.MAT_NO_NEW_DIAGONALS
        YES_NEW_DIAGONALS          = _petsc.MAT_YES_NEW_DIAGONALS
        INODE_LIMIT_1              = _petsc.MAT_INODE_LIMIT_1
        INODE_LIMIT_2              = _petsc.MAT_INODE_LIMIT_2
        INODE_LIMIT_3              = _petsc.MAT_INODE_LIMIT_3
        INODE_LIMIT_4              = _petsc.MAT_INODE_LIMIT_4
        INODE_LIMIT_5              = _petsc.MAT_INODE_LIMIT_5
        IGNORE_OFF_PROC_ENTRIES    = _petsc.MAT_IGNORE_OFF_PROC_ENTRIES
        ROWS_UNSORTED              = _petsc.MAT_ROWS_UNSORTED
        COLUMNS_UNSORTED           = _petsc.MAT_COLUMNS_UNSORTED
        NEW_NONZERO_LOCATION_ERR   = _petsc.MAT_NEW_NONZERO_LOCATION_ERR
        NEW_NONZERO_ALLOCATION_ERR = _petsc.MAT_NEW_NONZERO_ALLOCATION_ERR
        USE_HASH_TABLE             = _petsc.MAT_USE_HASH_TABLE
        KEEP_ZEROED_ROWS           = _petsc.MAT_KEEP_ZEROED_ROWS
        IGNORE_ZERO_ENTRIES        = _petsc.MAT_IGNORE_ZERO_ENTRIES
        USE_INODES                 = _petsc.MAT_USE_INODES
        DO_NOT_USE_INODES          = _petsc.MAT_DO_NOT_USE_INODES
        NOT_SYMMETRIC              = _petsc.MAT_NOT_SYMMETRIC
        HERMITIAN                  = _petsc.MAT_HERMITIAN
        NOT_STRUCTURALLY_SYMMETRIC = _petsc.MAT_NOT_STRUCTURALLY_SYMMETRIC
        NOT_HERMITIAN              = _petsc.MAT_NOT_HERMITIAN
        SYMMETRY_ETERNAL           = _petsc.MAT_SYMMETRY_ETERNAL
        NOT_SYMMETRY_ETERNAL       = _petsc.MAT_NOT_SYMMETRY_ETERNAL
        USE_COMPRESSEDROW          = _petsc.MAT_USE_COMPRESSEDROW
        DO_NOT_USE_COMPRESSEDROW   = _petsc.MAT_DO_NOT_USE_COMPRESSEDROW
        IGNORE_LOWER_TRIANGULAR    = _petsc.MAT_IGNORE_LOWER_TRIANGULAR
        ERROR_LOWER_TRIANGULAR     = _petsc.MAT_ERROR_LOWER_TRIANGULAR
        GETROW_UPPERTRIANGULAR     = _petsc.MAT_GETROW_UPPERTRIANGULAR
              
    class InfoType:
        """
        Indicate if you want information about the local part of the
        matrix, the entire parallel matrix or the maximum over all the
        local parts.
        """
        LOCAL      = _petsc.MAT_LOCAL
        GLOBAL_MAX = _petsc.MAT_GLOBAL_MAX
        GLOBAL_SUM = _petsc.MAT_GLOBAL_SUM
        
    class AssemblyType:
        """
        Indicate if the matrix is now to be used, or if you plan to
        continue to add values to it.
        """
        # native
        FINAL_ASSEMBLY = _petsc.MAT_FINAL_ASSEMBLY
        FLUSH_ASSEMBLY = _petsc.MAT_FLUSH_ASSEMBLY
        # aliases
        FINAL = FINAL_ASSEMBLY
        FLUSH = FLUSH_ASSEMBLY

    class OrderingType:
        """
        Orderings for reduce fill-in or to improve numerical stability
        of matrix factorization.

          + NATURAL: Natural ordering.
          + ND:      Nested Dissection.
          + OWD:     One-way Dissection.
          + RCM:     Reverse Cuthill-McKee.
          + QMD:     Quotient Minimum Degree.
        """
        NATURAL     = _petsc.MATORDERING_NATURAL
        ND          = _petsc.MATORDERING_ND
        OWD         = _petsc.MATORDERING_OWD
        RCM         = _petsc.MATORDERING_RCM
        QMD         = _petsc.MATORDERING_QMD
        ROWLENGTH   = _petsc.MATORDERING_ROWLENGTH
        DSC_ND      = _petsc.MATORDERING_DSC_ND
        DSC_MMD     = _petsc.MATORDERING_DSC_MMD
        DSC_MDF     = _petsc.MATORDERING_DSC_MDF
        CONSTRAINED = _petsc.MATORDERING_CONSTRAINED
        IDENTITY    = _petsc.MATORDERING_IDENTITY
        REVERSE     = _petsc.MATORDERING_REVERSE

    class Structure:
        """
        Indicate if the matrix has the same nonzero structure.
        """
        # native
        SAME_NONZERO_PATTERN      = _petsc.SAME_NONZERO_PATTERN
        DIFFERENT_NONZERO_PATTERN = _petsc.DIFFERENT_NONZERO_PATTERN
        SUBSET_NONZERO_PATTERN    = _petsc.SUBSET_NONZERO_PATTERN
        SAME_PRECONDITIONER       = _petsc.SAME_PRECONDITIONER
        # aliases
        SAME      = SAME_NZ      = SAME_NONZERO_PATTERN
        SUBSET    = SUBSET_NZ    = SUBSET_NONZERO_PATTERN
        DIFFERENT = DIFFERENT_NZ = DIFFERENT_NONZERO_PATTERN
        SAMEPC    = SAME_PC      = SAME_PRECONDITIONER

    def __init__(self, *targs, **kwargs):
        super(Mat, self).__init__(*targs, **kwargs)
        
    def __iter__(self):
        """cannot iterate over matrices"""
        raise TypeError('cannot iterate over matrices')

    def __getitem__(self, ij):
        """Similar to `getValues()`"""
        i, j = ij
        if isinstance(i, int) and isinstance(j, int):
            return self.getValue(i, j)
        msize  = _petsc.MatGetSize(self)
        arange = _numpy.arange
        dtype  = _petsc.PetscInt
        if isinstance(i, slice):
            start, stop, stride = i.indices(msize[0])
            i = arange(start, stop, stride, dtype)
        if isinstance(j, slice):
            start, stop, stride = j.indices(msize[1])
            j = arange(start, stop, stride, dtype)
        return self.getValues(i, j)

    def __setitem__(self, ij, v):
        """Similar to `setValues()`"""
        i, j = ij
        msize  = _petsc.MatGetSize(self)
        arange = _numpy.arange
        dtype  = _petsc.PetscInt
        if isinstance(i, slice):
            start, stop, stride = i.indices(msize[0])
            i = arange(start, stop, stride, dtype)
        if isinstance(j, slice):
            start, stop, stride = j.indices(msize[1])
            j = arange(start, stop, stride, dtype)
        self.setValues(i, j, v)

    def __call__(self, x, y):
        """Same as `mult()`"""
        self.mult(x, y)

    # unary operations
    __pos__ = _matops.__pos__
    __neg__ = _matops.__neg__
    # binary operations
    __add__ = _matops.__add__
    __sub__ = _matops.__sub__
    __mul__ = _matops.__mul__
    __div__ = _matops.__div__
    # inplace binary operations
    __iadd__ = _matops.__iadd__
    __isub__ = _matops.__isub__
    __imul__ = _matops.__imul__
    __idiv__ = _matops.__idiv__
    # reflected binary operations
    __radd__ = _matops.__radd__
    __rsub__ = _matops.__rsub__
    __rmul__ = _matops.__rmul__
    # true division operatios
    __truediv__  = _matops.__truediv__ 
    __itruediv__ = _matops.__itruediv__

    def create(self, comm=None):
        """
        Create an empty matrix object. The local and global row and
        column sizes can be set with `setSizes()` and the type can
        then be set with `setType()` (or perhaps `setFromOptions()`).

        .. note:: If you never call `setSizes()` and `setType()` it
           will generate an error when you try to use the matrix.
        """
        return _petsc.MatCreate(comm, self)
        
    def createDense(self, size, comm=None):
        """
        """
        if _petsc.PetscCommGetSize(comm) == 1:
            return self.createSeqDense(size, comm)
        else:
            return self.createMPIDense(size, comm)
        
    def createSeqDense(self, size, comm=None):
        """
        """
        comm, m, n = _petsc.matseq_sizes(comm, size)
        return _petsc.MatCreateSeqDense(comm, m, n, self)

    def createMPIDense(self, size, comm=None):
        """
        """
        comm, m, n, M, N = _petsc.matmpi_sizes(comm, size)
        return _petsc.MatCreateMPIDense(comm, m, n, M, N, self)

    def createAIJ(self, size, bsize=None,
                  nz=None, d_nz=None, o_nz=None, csr=None,
                  comm=None):
        """
        """
        if _petsc.PetscCommGetSize(comm) == 1:
            if nz is None:
                nz = d_nz
            return self.createSeqAIJ(size, bsize, nz, csr, comm)
        else:
            if d_nz is None:
                d_nz = nz
            return self.createMPIAIJ(size, bsize,
                                     d_nz, o_nz, csr,
                                     comm, self)
        
    def createSeqAIJ(self, size, bsize=None,
                     nz=None, csr=None,
                     comm=None):
        """
        """
        # communicator and sizes
        comm, m, n  = _petsc.matseq_sizes(comm, size, bsize)
        # matrix type
        if bsize is None:
            mattype = _petsc.MATSEQAIJ
        else:
            mattype = _petsc.MATSEQBAIJ
        # preallocation
        if csr is None:
            nz, nnz = _petsc.mataij_nz(m, nz, bsize)
            if bsize is None:
                preallocate = _petsc.MatSeqAIJSetPreallocation
                allocdata = nz, nnz
            else:
                preallocate = _petsc.MatSeqBAIJSetPreallocation
                allocdata = bsize, nz, nnz
        else:
            i, j, v  = _petsc.mataij_csr(m, csr, bsize)
            if bsize is None:
                preallocate = _petsc.MatSeqAIJSetPreallocationCSR
                allocdata = i, j, v
            else:
                preallocate = _petsc.MatSeqBAIJSetPreallocationCSR
                allocdata = bsize, i, j, v
        # create matrix
        _petsc.MatCreate(comm, self)
        _petsc.MatSetSizes(self, m, n, m, n)
        _petsc.MatSetType(self, mattype)
        preallocate(self, *allocdata)
        return self
        
    def createMPIAIJ(self, size, bsize=None,
                     d_nz=None, o_nz=None, csr=None,
                     comm=None):
        """
        """
        # communicator and sizes
        comm, m, n, M, N = _petsc.matmpi_sizes(comm, size, bsize)
        # matrix type
        if bsize is None:
            mattype = _petsc.MATMPIAIJ
        else:
            mattype = _petsc.MATMPIBAIJ
        # preallocation
        if csr is None:
            d_nz, d_nnz = _petsc.mataij_nz(m, d_nz, bsize)
            o_nz, o_nnz = _petsc.mataij_nz(m, o_nz, bsize)
            if bsize is None:
                preallocate = _petsc.MatMPIAIJSetPreallocation
                allocdata = d_nz, d_nnz, o_nz, o_nnz
            else:
                preallocate = _petsc.MatMPIBAIJSetPreallocation
                allocdata = bsize, d_nz, d_nnz, o_nz, o_nnz
        else:
            i, j, v  = _petsc.mataij_csr(m, csr, bsize)
            if bsize is None:
                preallocate = _petsc.MatMPIAIJSetPreallocationCSR
                allocdata   = i, j, v
            else:
                preallocate = _petsc.MatMPIBAIJSetPreallocationCSR
                allocdata   = bsize, i, j, v
        # create matrix
        _petsc.MatCreate(comm, self)
        _petsc.MatSetSizes(self, m, n, M, N)
        _petsc.MatSetType(self, mattype)
        preallocate(self, *allocdata)
        return self

    def createSBAIJ(self, size, bsize=None,
                    nz=None, d_nz=None, o_nz=None,
                    comm=None):
        """
        """
        if _petsc.PetscCommGetSize(comm) == 1:
            if nz is None:
                nz = d_nz
            return self.createSeqSBAIJ(size, bsize, nz,
                                       comm)
        else:
            if d_nz is None:
                d_nz = nz
            return self.createMPISBAIJ(size, bsize, d_nz, o_nz, comm)
        
    def createSeqSBAIJ(self, size, bsize=None, nz=None, comm=None):
        """
        """
        # default block size
        if bsize is None:
            bsize = 1
        # communicator and sizes
        comm, m, n  = _petsc.matseq_sizes(comm, size, bsize)
        # matrix type
        mattype = _petsc.MATSEQSBAIJ
        # preallocation
        nz, nnz = _petsc.mataij_nz(m, nz, bsize)
        preallocate = _petsc.MatSeqSBAIJSetPreallocation
        allocdata = bsize, nz, nnz
        # create matrix
        _petsc.MatCreate(comm, self)
        _petsc.MatSetSizes(self, m, n, m, n)
        _petsc.MatSetType(self, mattype)
        preallocate(self, *allocdata)
        return self
        
    def createMPISBAIJ(self, size, bsize=None,
                       d_nz=None, o_nz=None,
                       comm=None):
        """
        """
        # default block size
        if bsize is None:
            bsize = 1
        # communicator and sizes
        comm, m, n, M, N = _petsc.matmpi_sizes(comm, size, bsize)
        # matrix type
        mattype = _petsc.MATMPISBAIJ
        # preallocation
        d_nz, d_nnz = _petsc.mataij_nz(m, d_nz, bsize)
        o_nz, o_nnz = _petsc.mataij_nz(m, o_nz, bsize)
        preallocate = _petsc.MatMPISBAIJSetPreallocation
        allocdata = bsize, d_nz, d_nnz, o_nz, o_nnz
        # create matrix
        _petsc.MatCreate(comm, self)
        _petsc.MatSetSizes(self, m, n, M, N)
        _petsc.MatSetType(self, mattype)
        preallocate(self, *allocdata)
        return self

    def createIS(self, size, lgmap, comm=None):
        """
        Create a *process unassmembled* matrix, it is assembled on
        each process but not across processes.

        :Parameters:
          - `size`: number of local and global rows and columns.
          - `lgmap`: local to global mapping.
          - `comm`:  MPI communicator (defaults to `COMM_WORLD`).
        """
        comm, m, n, M, N = _petsc.matmpi_sizes(comm, size)
        return _petsc.MatCreateIS(comm, m, n, M, N, lgmap, self)

    def createNormal(self, matrix):
        """
        Create a matrix that behaves like A'*A.

        :Parameters:
          - `matrix`: Matrix A (possibly rectangular) to form A'*A
            operator.

        :Returns:
          - the created normal matrix.

        .. note:: The product A'*A is NOT actually formed! Rather the
           new matrix object performs the matrix-vector product by
           first multiplying vectors by A and then A'.
       """
        return _petsc.MatCreateNormal(matrix, self)

    def createScatter(self, scatter, comm=None):
        """
        Create a new matrix based on a VecScatter.

        :Parameters:
          - `scatter`: a VecScatter instance.

        :Returns:
          - the created scatter matrix.
       """
        if comm is None:
            comm = _petsc.PetscObjectGetComm(scatter)
        return _petsc.MatCreateScatter(comm, scatter, self)

    def createShell(self, size, context, comm=None):
        """
        Create a shell matrix to be used to define your own matrix
        type (perhaps matrix free).

        :Parameters:
          - `size`: number of local and global rows and columns.
          - `context`: user-defined context object implementig the
            matrix interface.
          - `comm`:  MPI communicator (defaults to `COMM_WORLD`).
              
        :Returns:
          - the created shell matrix.

        .. note:: PETSc requires that matrices and vectors being used
           for certain operations are partitioned accordingly.  For
           example, when creating a shell matrix, A, that supports
           parallel matrix-vector products using A.mult(x,y) the user
           should set the number of local matrix rows to be the number
           of local elements of the corresponding result vector,
           y. Note that this information is required for use of the
           matrix interface routines, even though the shell matrix may
           not actually be physically partitioned.

        """
        comm, m, n, M, N = _petsc.matmpi_sizes(comm, size)
        return _petsc.MatCreateShell(comm, m, n, M, N,
                                     context, self)

    def getSize(self):
        """
        Return the global number of rows and columns in a matrix.

        :Returns:
          - the number of global rows.
          - the number of global columns.
        """
        return tuple(_petsc.MatGetSize(self))

    def getLocalSize(self):
        """
        Return the local number of rows and columns in a matrix.
   
        :Returns:
          - the number of local rows.
          - the number of local columns.

        .. caution:: This information may be implementation dependent.
        """
        return tuple(_petsc.MatGetLocalSize(self))

    def getSizes(self):
        """
        Return the local and global number of rows and columns in a
        matrix.

        :Returns:
          - a tuple with the number of local rows and columns.
          - a tuple with the number of global rows and columns.
        """
        lsize = tuple(_petsc.MatGetLocalSize(self))
        gsize = tuple(_petsc.MatGetSize(self))
        return (lsize, gsize)

    def setSizes(self, sizes, bsize=None):
        """
        Set the local and global number of rows and columns, and check
        to determine compatibility.
        """
        comm = _petsc.PetscObjectGetComm(self)
        if _petsc.PetscCommGetSize(comm) == 1:
            comm, m, n  = _petsc.matseq_sizes(comm, sizes, bsize)
            M, N = m, n
        else:
            comm, m, n, M, N = _petsc.matmpi_sizes(comm, sizes, bsize)
        _petsc.MatSetSizes(self, m, n, M, N)
        if bsize is not None:
            _petsc.MatSetBlockSize(self, bsize)

    def getBlockSize(self):
        """
        Return the matrix block size; useful especially for the block
        row and block diagonal formats.
        """
        return _petsc.MatGetBlockSize(self)
    
    def setBlockSize(self, bsize):
        """
        Set the matrix block size; for many matrix types you cannot
        use this and MUST set the blocksize when you preallocate the
        matrix.
        
        :Parameters:
          - `bs`: block size.

        .. note:: Only works for shell and AIJ matrices.
        """
        bsize = _petsc.obj_bsize(bsize)
        _petsc.MatSetBlockSize(self, bsize)

    def getOwnershipRange(self):
        """
        Return the range of matrix rows owned by this processor,
        assuming that the matrix is laid out with the first *n1* rows
        on the first processor, the next *n2* rows on the second, etc.

        :Returns:
          - the global index of the first local row.
          - one more than the global index of the last local row.

        .. caution:: For certain parallel layouts this range may not
           be well defined.

        """
        return tuple(_petsc.MatGetOwnershipRange(self))

    def setOption(self, option):
        """
        Set parameter options for a matrix. Some options may be
        specific to certain storage formats.
        """
        try:
            options = iter(option)
        except TypeError:
            options = (option,)
        for option in options:
            opt = _petsc.get_attr(Mat.Option, option)
            _petsc.MatSetOption(self, opt)

    def setPreallocation(self, nz=None, csr=None):
        """
        """
        _petsc.MatSetPreallocation(self, nz, csr)

    def setPreallocationNZ(self, nz):
        """
        """
        _petsc.MatSetPreallocation(self, nz, None)

    def setPreallocationCSR(self, csr):
        """
        """
        _petsc.MatSetPreallocation(self, None, csr)
            
    def setUpPreallocation(self):
        """
        """
        _petsc.MatSetUpPreallocation(self)

    def duplicate(self, copy_values=False):
        """
        Duplicate a matrix structure, and optionally copies its
        values.
        """
        if copy_values:
            copy = _petsc.MAT_COPY_VALUES
        else:
            copy = _petsc.MAT_DO_NOT_COPY_VALUES
        return _petsc.MatDuplicate(self, copy)

    def copy(self, mat=None, structure=None):
        """
        Copy a matrix structure and its values.
        """
        if mat is None:
            return _petsc.MatDuplicate(self, _petsc.MAT_COPY_VALUES)
        else:
            structure = _petsc.get_attr(Mat.Structure, structure)
            if structure is None:
                structure = _petsc.DIFFERENT_NONZERO_PATTERN
            elif structure != _petsc.DIFFERENT_NONZERO_PATTERN:
                if structure != _petsc.SAME_NONZERO_PATTERN:
                    raise ValueError('invalid value for `structure`')
            _petsc.MatCopy(self, mat, structure)
            return mat

    @staticmethod
    def Load(viewer, mat_type=None):
        """
        Load a matrix that has been stored in binary format with
        `Mat.view()`. Generate a parallel MPI matrix if the
        communicator has more than one processor.  The default matrix
        type is AIJ.
        """
        mat_type = _petsc.get_attr(Mat.Type, mat_type)
        return _petsc.MatLoad(viewer, mat_type)

    def convert(self, mat_type, result=None):
        """
        Convert a matrix to another matrix, either of the same
        or different type.
        """
        mat_type = _petsc.get_attr(Mat.Type, mat_type)
        return _petsc.MatConvert(self, mat_type, result)

    def compress(self):
        """
        Try to store the matrix in as little space as possible. May
        fail if memory is already fully used, since it tries to
        allocate new space.
        """
        _petsc.MatCompress(self)

    def computeExplicitOperator(self):
        """
        Compute the explicit matrix

        .. note:: This computation is done by applying the operators
           to columns of the identity matrix.
        """
        return _petsc.MatComputeExplicitOperator(self)
    
    def equal(self, mat):
        """
        Compare two matrices.
        """
        return bool(_petsc.MatEqual(self, mat))

    def isTranspose(self, mat=None, tol=0.0):
        """
        Test whether a matrix is another one's transpose, 
        or its own, in which case it tests symmetry.
        """
        if  mat is None:
            mat = self
        return bool(_petsc.MatIsTranspose(self, mat, tol))

    def isSymmetric(self, tol=0.0):
        """
        Test whether a matrix is symmetric
        """
        return bool(_petsc.MatIsSymmetric(self, tol))

    def isSymmetricKnown(self):
        """
        Checks the flag on the matrix to see if it is symmetric.
        """
        rslt = _petsc.MatIsSymmetricKnown(self)
        return tuple(bool(i) for i in rslt)

    def isStructurallySymmetric(self):
        """
        Test whether a matrix is structurally symmetric.
        """
        return bool(_petsc.MatIsStructurallySymmetric(self))

    def isHermitian(self):
        """
        Test whether a matrix is Hermitian, i.e. it is the complex
        conjugate of its transpose.
        """
        return bool(_petsc.MatIsHermitian(self))

    def isHermitianKnown(self):
        """
        Checks the flag on the matrix to see if it is hermitian.
        """
        rslt = _petsc.MatIsHermitianKnown(self)
        return tuple(bool(i) for i in rslt)

    def getColumnVector(self, vec, col):
        """
        Get the values from a given column of a matrix.

        .. note:: Each processor for which this is called gets the
           values for its rows. The vector must have the same parallel
           row layout as the matrix. Since PETSc matrices are usually
           stored in compressed row format, this routine will
           generally be slow.
        """
        _petsc.MatGetColumnVector(self, vec, col)

    def getValue(self, row, col):
        """
        Get a single entry from a matrix.
        """
        return _petsc.MatGetValue(self, row, col)

    def getValues(self, rows, cols, values=None):
        """
        Get a block of values from a matrix.
        """
        if values is None:
            rows = _numpy.asarray(rows, _petsc.PetscInt)
            cols = _numpy.asarray(cols, _petsc.PetscInt)
            shape = (_numpy.size(rows), _numpy.size(cols))
            values = _numpy.empty(shape, _petsc.PetscScalar)
            retval = values
        else:
            retval = None
        _petsc.MatGetValues(self, rows, cols, values)
        return retval

    def setValue(self, row, col, value, insert_mode=None):
        """
        Set a single entry from a matrix.
        """
        _petsc.MatSetValue(self, row, col, value, insert_mode)

    def setValues(self, rows, cols, values, insert_mode=None):
        """
        Set a block of values from a matrix.
        """
        _petsc.MatSetValues(self, rows, cols, values, insert_mode)

    def setValuesCSR(self, I, J, V, insert_mode=None):
        """
        """
        _petsc.MatSetValuesCSR(self, I, J, V, insert_mode)
        
    def setLGMapping(self, lgmap):
        """
        Set a local-to-global numbering for use by `setValuesLocal()`
        to allow users to insert matrix entries using a local
        (per-processor) numbering.
        """
        _petsc.MatSetLocalToGlobalMapping(self, lgmap)

    def setValueLocal(self, row, col, value, insert_mode=None):
        """
        Set a single entry from a matrix using a local
        (per-processor) numbering..
        """
        return _petsc.MatSetValueLocal(self, row, col, value,
                                       insert_mode)
    
    def setValuesLocal(self, rows, cols, values, insert_mode=None):
        """
        Set a block of values from a matrix using a local
        (per-processor) numbering.
        """
        _petsc.MatSetValuesLocal(self, rows, cols, values,
                                 insert_mode)
        
    def setValuesBlocked(self, rows, cols, values, insert_mode=None):
        """
        Inserts or adds a block of values into a matrix.
        """
        return _petsc.MatSetValuesBlocked(self, rows, cols, values,
                                          insert_mode)

    def setLGMappingBlock(self, lgmap):
        """
        Set a local-to-global numbering for use by
        `setValuesBlockedLocal()` to allow users to insert matrix
        entries using a local (per-processor) numbering.
        """
        _petsc.MatSetLocalToGlobalMappingBlock(self, lgmap)

    def setValuesBlockedLocal(self, rows, cols, values,
                              insert_mode=None):
        """
        Inserts or adds values into certain locations of a matrix,
        using a local ordering of the nodes a block at a time.
        """
        _petsc.MatSetValuesBlockedLocal(self, rows, cols, values,
                                        insert_mode)

    def storeValues(self):
        """
        Stashes a copy of the matrix values.

        .. tip:: This allows reuse of the linear part of
           a Jacobian, while recomputing the nonlinear portion.
        """
        _petsc.MatStoreValues(self)
        
    def retrieveValues(self):
        """
        Retrieves the copy of the matrix values.

        .. tip:: This allows reuse of the linear part of
           a Jacobian, while recomputing the nonlinear portion.
        """
        _petsc.MatRetrieveValues(self)
    
    def assemblyBegin(self, assembly=None):
        """
        Begins assembling the matrix.  This routine should
        be called after completing all calls to `SetValues()`.
        """
        _petsc.MatAssemblyBegin(self, assembly)

    def assemblyEnd(self, assembly=None):
        """
        Completes assembling the matrix.  This routine should
        be called after `AssemblyBegin()`.
        """
        _petsc.MatAssemblyEnd(self, assembly)

    def assemble(self, assembly=None):
        """
        Calls ``AssemblyBegin()` and `AssemblyEnd()`.
        """
        _petsc.MatAssemblyBegin(self, assembly)
        _petsc.MatAssemblyEnd(self, assembly)

    def isAssembled(self):
        """
        Indicates if a matrix has been assembled and is ready for use,
        for example, in matrix-vector product.
        """
        return bool(_petsc.MatAssembled(self))

    assembled = isAssembled

    def getRowIJ(self, symmetric=False):
        """
        Returns the compressed row storage i and j indices for
        sequential matrices.
        """
        return tuple(_petsc.MatGetRowIJ(self, symmetric))

    def getColumnIJ(self, symmetric=False):
        """
        Returns the compressed column storage i and j indices for
        sequential matrices.
        """
        return tuple(_petsc.MatGetColumnIJ(self, symmetric))

    def setNullSpace(self, nullsp):
        """
        Attaches a null space to a matrix.  This null space will be
        removed from the resulting vector whenever `Mult()` is
        called.

        :Parameters:
        - `nullsp`: the null space object.

        .. note:: Overwrites any previous null space that may have
           been attached.
        """
        _petsc.MatNullSpaceAttach(self, nullsp)

    attachNullSpace = setNullSpace

    def getVecs(self):
        """
        Get vectors compatible with the matrix, i.e. with the same 
        parallel layout.

        :Returns:
          - `right`: vector that the matrix can be multiplied against.
          - `left`: vector that the matrix vector product can be
            stored in.
        """
        return _petsc.MatGetVecs(self)

    def getVecLeft(self):
        """
        Get a vector that the matrix vector product can be stored in.
        """
        return _petsc.MatGetVecLeft(self)

    def getVecRight(self):
        """
        Get vector that the matrix can be multiplied against.
        """
        return _petsc.MatGetVecRight(self)

    def mult(self, x, y):
        """
        A * x -> y
        """
        _petsc.MatMult(self, x, y)

    def multAdd(self, v1, v2, v3):
        """
        A * v1 + v2 -> v3
        """
        _petsc.MatMultAdd(self, v1, v2, v3)

    def multTranspose(self, x, y):
        """
        A' * x -> y
        """
        _petsc.MatMultTranspose(self, x, y)

    def multTransposeAdd(self, v1, v2, v3):
        """
        A' * v1 + v2 -> v3
        """
        _petsc.MatMultTransposeAdd(self, v1, v2, v3)

    def multConstrained(self, x, y):
        """
        The inner multiplication routine for a constrained matrix
        P' A P.
        """
        _petsc.MatMultConstrained(self, x, y)
    
    def multTransposeConstrained(self, x, y):
        """
        The inner multiplication routine for a constrained matrix
        P' A' P.
        """
        _petsc.MatMultTransposeConstrained(self, x, y)

    def getDiagonal(self, diag):
        """
        Get the diagonal of a matrix in a vector, A[i,i] -> diag[i]

        :Parameters:
          - `vec`: the vector for storing the diagonal.

        .. note:: For the `SEQAIJ` matrix format, this routine may
           also be called on a LU factored matrix; in that case it
           routines the reciprocal of the diagonal entries in U. It
           returns the entries permuted by the row and column
           permutation used during the symbolic factorization.
        """
        _petsc.MatGetDiagonal(self, diag)

    def getRowMax(self, vec):
        """
        Get the maximum value (in absolute value) of each row of the
        matrix
        """
        _petsc.MatGetRowMax(self, vec)

    def conjugate(self):
        """
        Replaces the matrix values with their complex conjugates.
        """
        _petsc.MatConjugate(self)

    def transpose(self, inplace=True):
        """
        Compute an in-place or out-of-place transpose of a matrix.
        
        :Parameters:
          - `inplace`: defaults to `True`.

        :Returns:
          - the transposed matrix, when `inplace` is `False`.
        """
        if inplace:
            _petsc.MatTranspose(self, 1)
        else:
            return _petsc.MatTranspose(self, 0)

    def permute(self, row_perm, col_perm):
        """
        Creates a new matrix with rows and columns permuted from the
        original.

        :Parameters:
          - `row_perm`: index set with row permutation, each
            processor supplies only the permutation for its rows.
          - `col_perm`: index set with column permutation, each
            processor needs the entire column permutation, that is
            this is the same size as the total number of columns in
            the matrix.
        """
        return _petsc.MatPermute(self, row_perm, col_perm)
        
        
    def permuteSparsify(self, band, frac, tol, row_perm, col_perm):
        """
        Creates a new matrix with rows and columns permuted from the
        original and sparsified to the prescribed tolerance.

        :Parameters:
          - `band`: the half-bandwidth of the sparsified matrix, or
            `DECIDE`.
          - `frac`: the half-bandwidth as a fraction of the total
            size, or 0.0.
          - `tol`: the drop tolerance
          - `row_perm`: index set with row permutation.
          - `col_perm`: index set with column permutation.
        """
        return _petsc.MatPermuteSparsify(self, band, frac, tol,
                                         row_perm, col_perm)

    def diagonalScale(self, L, R):
        """
        Scales a matrix on the left and right by diagonal matrices
        that are stored as vectors.  Either of the two scaling
        matrices can be ``None``.

        :Parameters:
          - `L`: the left  scaling vector (or ``None``).
          - `R`: the right scaling vector (or ``None``).

        .. note:: `diagonalScale()` computes A = LAR, where L is a
           diagonal matrix and R is a diagonal matrix.
        """
        _petsc.MatDiagonalScale(self, L, R)

    def diagonalSet(self, D, insert_mode=None):
        """
        Compute Y <- Y + D (where D is a diagonal matrix that is
        represented as a vector), or Y[i,i] <- D[i] (if insertion mode
        is `INSERT_VALUES`).

        :Parameters:
          - `D`: the vector representing a diagonal matrix.
          - `insert_mode`: either `INSERT_VALUES` or `ADD_VALUES`
        """
        _petsc.MatDiagonalSet(self, D, insert_mode)

    def norm(self, norm_type=None):
        """
        Calculates various norms of a matrix.

        :Parameters:
          - `type`: the norm type,
            + 'NormType.NORM_1',
            + 'NormType.NORM_FROBENIUS'
            + 'NormType.NORM_INFINITY'.

        :Returns:
          - the resulting norm value.
        """
        return _petsc.MatNorm(self, norm_type)

    def zeroEntries(self):
        """
        Zeros all entries of a matrix.  For sparse matrices this
        routine retains the old nonzero structure.
        """
        _petsc.MatZeroEntries(self)

    def zeroRows(self, rows, diag=1.0):
        """
        Zeros all entries (except possibly the main diagonal) of a set
        of rows of a matrix.

        :Parameters:
          - `rows`: index set of rows to remove.
          - `diag`: value to put in all diagonals of eliminated rows,
            defaults to 1.

        .. note:: For the `AIJ` and `BAIJ` matrix formats this removes
           the old nonzero structure, but does not release memory.
           For the dense and block diagonal formats this does not
           alter the nonzero structure.

           If the option `Option.KEEP_ZEROED_ROWS` is set with
           `setOption()` the nonzero structure of the matrix is not
           changed (even for `AIJ` and `BAIJ` matrices) the values are
           merely zeroed.

           The user can set a value in the diagonal entry (or for the
           `AIJ` and row formats can optionally remove the main
           diagonal entry from the nonzero structure as well, by
           passing 0.0 for `diag` argument).
           
           For the parallel case, all processes that share the matrix
           (i.e., those in the communicator used for matrix creation)
           MUST call this routine, regardless of whether any rows
           being zeroed are owned by them.
        """
        _petsc.MatZeroRows(self, rows, diag)

    def zeroRowsLocal(self, rows, diag=1.0):
        """
        Zeros all entries (except possibly the main diagonal) of a set
        of rows of a matrix; using local numbering of rows.

        :Parameters:
          - `isrow`: index set of rows to remove
          - `diag`: value to put in all diagonals of eliminated rows.

        .. note:: Before calling `ZeroRowsLocal`(), the user must
           first set the local-to-global mapping by calling
           `setLGMapping()`.

           For the `AIJ` matrix formats this removes the old nonzero
           structure, but does not release memory.  For the dense and
           block diagonal formats this does not alter the nonzero
           structure.

           If the option `Mat.KEEP_ZEROED_ROWS` the nonzero
           structure of the matrix is not changed (even for `AIJ` and
           `BAIJ` matrices) the values are merely zeroed.

           The user can set a value in the diagonal entry (or for the
           `AIJ` and row formats can optionally remove the main
           diagonal entry from the nonzero structure as well, by
           passing 0.0 for `diag` argument).
        """
        _petsc.MatZeroRowsLocal(self, rows, diag)

    @staticmethod
    def merge(mat, outmat=None, comm=None, csize=None):
        """
        Creates a single large PETSc matrix by concatenating
        sequential matrices from each processor
        """
        if csize is None:
            csize = _petsc.PETSC_DECIDE
        return _petsc.MatMerge(comm, mat, csize, outmat)

    def getSubMatrix(self, isrow, iscol, submat=None, csize=None):
        """
        Get a single submatrix on the same number of processors as
        the original matrix.

        :Parameters:
          - `isrow`: rows this processor should obtain.
          - `iscol`: columns for all processors you wish to keep.
          - `csize`: number of columns *local* to this processor
            (does nothing for sequential matrices). This should
            match the result from `Vec.GetLocalSize()` if you
            plan to use the matrix in a A*x; alternatively, you can
            use `DECIDE`.
           
        :Returns:
          - the new submatrix, of the same type as the old.

        .. note:: The `iscol` argument MUST be the same on each
           processor. You might be able to create the `iscol` argument
           with `is.AllGather()`.
        """
        if csize is None:
            csize = _petsc.PETSC_DECIDE
        return _petsc.MatGetSubMatrix(self, isrow, iscol,
                                      csize, submat)


    def getSubMatrixSeq(self, isrow, iscol, submat=None):
        """
        Get a sequential submatrix.
        """
        return _petsc.MatGetSubMatrixSeq(self, isrow, iscol, submat)

    def increaseOverlap(self, iset, overlap=1):
        """
        Given a submatrix indicated by an index set, replaces the
        index set by a larger one that represent a submatrix with
        additional overlap.
        """
        return _petsc.MatIncreaseOverlap(self, iset, overlap)

    def scale(self, alpha):
        """
        Scales all elements of a matrix by a given number.

        A[i,j] <- alpha * A[i,j]

        :Parameters:
          - `alpha`: the scalar.
        """
        _petsc.MatScale(self, alpha)
     
    def shift(self, alpha):
        """
        Adds a scalar value to the entries in the diagonal of a
        matrix.

        A[i,i] <-  A[i,i] + alpha 
        
        :Parameters:
          - `alpha`: the scalar.
        """
        _petsc.MatShift(self, alpha)

    def axpy(self, alpha, X, matstr=None):
        """
        Compute Y <- a*X + Y.

        Y[i,j] <- alpha * X[i,j] + Y[i,j]

        :Parameters:
          - `alpha`: the scalar multiplier
          - `X`: the matrix.
          - `matstr`: either `SAME_NONZERO_PATTERN`,
            `DIFFERENT_NONZERO_PATTERN` or `SUBSET_NONZERO_PATTERN`
        """
        if matstr is None:
            matstr = _petsc.DIFFERENT_NONZERO_PATTERN
        else:
            matstr = _petsc.get_attr(Mat.Structure, matstr)
        _petsc.MatAXPY(self, alpha, X, matstr)

    def aypx(self, alpha, X):
        """
        Compute Y = a*Y + X.

        Y[i,j] <- alpha * Y[i,j] + X[i,j]
        
        :Parameters:
          - `alpha`: the scalar multiplier
          - `X`: the matrix.
          - `matstr`: either `SAME_NONZERO_PATTERN`,
            `DIFFERENT_NONZERO_PATTERN` or `SUBSET_NONZERO_PATTERN`
        """
        if matstr is None:
            matstr = _petsc.DIFFERENT_NONZERO_PATTERN
        else:
            matstr = _petsc.get_attr(Mat.Structure, matstr)
        _petsc.MatAYPX(self, alpha, X, matstr=None)

    AXPY  = axpy
    AYPX  = aypx
    
    def matMult(self, mat, result=None, fill=1.0):
        """
        Perform matrix-matrix multiplication C=A*B.
        """
        return _petsc.MatMatMult(self, mat, fill, result)
        
    def matMultSymbolic(self, mat, fill=1.0):
        """
        Perform construction, preallocation, and computes the ij
        structure of the matrix-matrix product C=A*B.  Call this
        method before calling `matMultNumeric()`.
        """
        return _petsc.MatMatMultSymbolic(self, mat, fill)
    
    def matMultNumeric(self, mat, result):
        """
        Perform the numeric matrix-matrix product.  Call this routine
        after first calling `matMultSymbolic()`.
        """
        _petsc.MatMatMultNumeric(self, mat, result)
        
    def matMultTranspose(self, mat, result=None, fill=1.0):
        """
        Perform matrix-matrix multiplication C=A^T*B.
        """
        return _petsc.MatMatMultTranspose(self, mat, fill, result)

    def interpolate(self, x, y):
        """
        Compute y <- A*x or A'*x depending on the shape of the matrix

        :Parameters:
          - `x`: the vector to restrict or interpolate.
          - `y`: the vector where the result is stored.

        .. note:: This allows one to use either the restriction or
           interpolation (its transpose) matrix to do the
           interpolation.
        """
        _petsc.MatInterpolate(self, x, y)

    def interpolateAdd(self, x, y, w):
        """
        Compute w <- y + A*x or A'*x depending on the shape of the
        matrix

        :Parameters:
          - `x`: the vector to restrict or interpolate.
          - `y`: the vector to add.
          - `w`: the vector where the result is stored.

        .. note:: Vector `w` may be the same vector as `y`.

        .. tip:: This allows one to use either the restriction or
           interpolation (its transpose) matrix to do the
           interpolation
        """
        _petsc.MatInterpolateAdd(self, x, y, w)

    def restrict(self, x, y):
        """
        Compute y <- A*x or A'*x

        :Parameters:
          - `x`: the vector to restrict or interpolate.
          - `y`: the vector where the result is stored.

        .. note:: This allows one to use either the restriction or
           interpolation (its transpose) matrix to do the restriction
        """
        _petsc.MatRestrict(self, x, y)
        
    def getOrdering(self, ord_type):
        """
        Get a reordering for a matrix to reduce fill or to improve
        numerical stability of LU factorization.

        :Parameters:
          - `type`: type of reordering, see `Mat.OrderingType`

        :Returns:
           - row permutation index set.
           - column permutation index set.

        .. note:: This DOES NOT actually reorder the matrix; it merely
           returns two index sets that define a reordering. This is
           usually not used directly, rather use the options
           `PCLU.setMatOrdering()` or `PCILU.setMatOrdering()`.
        """
        if type(ord_type) is str:
            if ord_type.lower() == '1wd':
                ord_type = 'owd'
        ord_type = _petsc.get_attr(Mat.OrderingType, ord_type)
        return _petsc.MatGetOrdering(self, ord_type)

    def reorderForNonzeroDiagonal(self, atol, isrow, iscol):
        """
        Changes matrix ordering to remove zeros from diagonal. This
        may help in the LU factorization to prevent a zero pivot.

        :Parameters:
          - `atol`: absolute tolerance.
          - `isrow`,`iscol` - index sets with row and column
            permutations.  Usually obtained from `getOrdering().`

        .. note:: This is not intended as a replacement for pivoting
           for matrices that have *bad* structure. It is only a
           stop-gap measure. Should be called after a call to
           `getOrdering()`, this routine changes the column ordering
           defined in iscol.
           Only works for `SEQAIJ` matrices.

        .. note:: Column pivoting is used, the algorithm is

           1) Choice of column is made by looking at the non-zero
              elements in the troublesome row for columns that are not
              yet included (moving from left to right).
 
           2) If (1) fails we check all the columns to the left of the
              current row and see if one of them has could be
              swapped. It can be swapped if its corresponding row has
              a non-zero in the column it is being swapped with; to
              make sure the previous nonzero diagonal remains nonzero
        """
        _petsc.MatReorderForNonzeroDiagonal(self, atol, isrow, iscol)


    class FactorInfo(_petsc.MatFactorInfo):

        """
        Options for matrix factorization routines.

        +------------------+-----------------------------------------+
        |       KEY        |                 MEANING                 |
        +==================+=========================================+
        | 'shiftnz'        | scaling of identity added to matrix to  |
        |                  | prevent zero pivots.                    |
        +------------------+-----------------------------------------+
        | 'shiftpd'        | if true, shift until positive pivots.   |
        +------------------+-----------------------------------------+
        | 'shift_fraction' | record shift fraction taken.            |
        +------------------+-----------------------------------------+
        | 'diagonal_fill'  | force diagonal to fill in if initially  |
        |                  | not filled.                             |
        +------------------+-----------------------------------------+
        | 'dt'             | drop tolerance.                         |
        +------------------+-----------------------------------------+
        | 'dtcol'          | tolerance for pivoting.                 |
        +------------------+-----------------------------------------+
        | 'dtcount'        | maximum nonzeros to be allowed per row. |
        +------------------+-----------------------------------------+
        | 'fill'           | expected fill nonzeros in factored      |
        |                  | matrix/nonzeros in original matrix.     |
        +------------------+-----------------------------------------+
        | 'levels'         | ICC/ILU levels.                         |
        +------------------+-----------------------------------------+
        | 'pivotinblocks'  | for BAIJ and SBAIJ matrices pivot in    |
        |                  | factorization on blocks, default        |
        |                  | 1.0, factorization may be faster if     |
        |                  | do not pivot.                           |
        +------------------+-----------------------------------------+
        | 'zeropivot'      | pivot is called zero if less than this. |
        +------------------+-----------------------------------------+
        """

        DEFAULT = {'shiftnz'        : 0.0,
                   'shiftpd'        : _petsc.PETSC_FALSE,
                   'shift_fraction' : 0.0,
                   'diagonal_fill'  : 0.0,
                   'dt'             : _petsc.PETSC_DEFAULT,
                   'dtcol'          : _petsc.PETSC_DEFAULT,
                   'dtcount'        : _petsc.PETSC_DEFAULT,
                   'fill'           : 5.0,
                   'levels'         : 0.0,
                   'pivotinblocks'  : 1.0,
                   'zeropivot'      : 1e-12 }
        """Default option values for matrix factorization routines"""


    def factorCholesky(self, isperm, options=None):
        """
        Perform in-place Cholesky factorization of a symmetric
        matrix.

        :Parameters:
          - `isperm`: index set with row and column permutations.
          - `options`: options for factorization, dictionary
            including the following keys:
              + 'fill' - expected fill as ratio of original fill.

        .. note:: See `LUFactor()` for the nonsymmetric case.

        .. tip:: Most users should employ the simplified KSP interface
           for linear solvers instead of working directly with matrix
           algebra routines such as this.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        _petsc.MatCholeskyFactor(self, isperm, factorinfo)
        return factorinfo

    def factorSymbolicCholesky(self, isperm, options=None):
        """
        Perform symbolic Cholesky factorization of a symmetric
        matrix. Call this method before calling
        `CholeskyFactorNumeric()`
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        func   = _petsc.MatCholeskyFactorSymbolic
        newmat = func(self, isperm, factorinfo)
        if options is not None:
            return newmat, factorinfo
        else:
            return newmat

    def factorNumericCholesky(self, mat, options=None):
        """
        Perform numeric Cholesky factorization of a symmetric
        matrix. Call this method after first calling
        `CholeskyFactorSymbolic()`.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        _petsc.MatCholeskyFactorNumeric(self, factorinfo, mat)
        return factorinfo


    def factorLU(self, isrow, iscol, options=None):
        """
        Perform in-place LU factorization of matrix.

        :Parameters:
          - `isrow`: index set with row permutation.
          - `iscol`: index set with column permutation.
          - `options`: options for factorization, dictionary
            including the following keys:
              + 'fill' : expected fill as ratio of original fill.
              + 'dtcol' : pivot tolerance (0 no pivot, 1 full column
                pivoting)

        .. note:: This changes the state of the matrix to a factored
           matrix; it cannot be used for example with `setValues()`
           unless one first calls `setUnfactored()`.

        .. tip:: Most users should employ the simplified `KSP`
           interface for linear solvers instead of working directly
           with matrix algebra routines such as this.

        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        _petsc.MatLUFactor(self, isrow, iscol, factorinfo)
        return factorinfo

    def factorSymbolicLU(self, isrow, iscol, options=None):
        """
        Perform symbolic LU factorization of matrix.  Call this
        method before calling `factorLUNumeric()`.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        func   = _petsc.MatLUFactorSymbolic
        newmat = func(self, isrow, iscol, factorinfo)
        if options is not None:
            return newmat, factorinfo
        else:
            return newmat

    def factorNumericLU(self, mat, options=None):
        """
        Perform numeric LU factorization of a matrix.  Call this
        routine after first calling `factorLUSymbolic()`.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        _petsc.MatLUFactorNumeric(self, factorinfo, mat)
        return factorinfo

    def factorICC(self, isperm, options=None):
        """
        Perform in-place incomplete Cholesky factorization of matrix.
        
        :Parameters:
          -  `isperm` : index set with row/column permutation.
          - `options`: options for factorization, dictionary
             including the following keys:
               + 'fill' : expected fill factor.
               + 'level' : level of fill, for ICC(level).

        .. note:: Probably really in-place only when level of fill is
           zero, otherwise allocates new space to store factored
           matrix and deletes previous memory.

        .. tip:: Most users should employ the simplified KSP interface
           for linear solvers instead of working directly with matrix
           algebra routines such as this.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        _petsc.MatICCFactor(self, isperm, factorinfo)
        return factorinfo

    def factorSymbolicICC(self, isperm, options=None):
        """
        Perform symbolic incomplete Cholesky factorization for a
        symmetric matrix.  Use `CholeskyFactorNumeric()` to complete
        the factorization.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        func   = _petsc.MatICCFactorSymbolic
        newmat = func(self, isperm, factorinfo)
        if options is not None:
            return newmat, factorinfo
        else:
            return newmat

    def factorILU(self, isrow, iscol, options=None):
        """
        Perform in-place ILU factorization of matrix.
        
        :Parameters:
          - `isrow`: index set with row permutation.
          - `iscol`: index set with column permutation.
          - `options`: options for factorization, dictionary including
            the following keys:
              + 'levels' : number of levels of fill.
              + 'fill' : expected as ratio of original fill.
              + 'diagonal_fill' : indicating force fill on diagonal
                (improves robustness for matrices missing diagonal
                entries).

        .. note:: Probably really in-place only when level of fill is
           zero, otherwise allocates new space to store factored
           matrix and deletes previous memory.

        .. tip:: Most users should employ the simplified KSP interface for
           linear solvers instead of working directly with matrix
           algebra routines such as this.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        _petsc.MatILUFactor(self, isrow, iscol, factorinfo)
        return factorinfo

    def factorSymbolicILU(self, isrow, iscol, options=None):
        """
        Perform symbolic ILU factorization of a matrix.  Uses levels
        of fill only, not drop tolerance. Use `LUFactorNumeric()` to
        complete the factorization.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        func   = _petsc.MatILUFactorSymbolic
        newmat = func(self, isrow, iscol, factorinfo)
        if options is not None:
            return newmat, factorinfo
        else:
            return newmat

    def factorILUDT(self, isrow, iscol, options=None):
        """
        Perform a drop tolerance ILU factorization.
        """
        if options is not None:
            factorinfo = self.FactorInfo(options)
        else:
            factorinfo = None
        newmat = _petsc.MatILUDTFactor(self, isrow, iscol,
                                       factorinfo)
        if options is not None:
            return newmat, factorinfo
        else:
            return newmat

    def setUnfactored(self):
        """
        Resets a factored matrix to be treated as unfactored.

        .. note:: This routine should be used only with factored
           matrices formed by in-place factorization via ILU(0) (or by
           in-place LU factorization for sequential dense matrices).
        """
        _petsc.MatSetUnfactored(self)

    def getInertia(self):
        """
        Get the inertia from a factored matrix.

        :Returns:
          - number of negative eigenvalues.
          - number of zero eigenvalues.
          - number of positive eigenvalues.
        """
        return tuple(_petsc.MatGetInertia(self))

    def forwardSolve(self, b, x):
        """
        Solve L x = b, given a factored matrix, A = LU.
        """
        _petsc.MatForwardSolve(self, b, x)

    def backwardSolve(self, b, x):
        """
        Solve U x = b, given a factored matrix, A = LU.
        """
        _petsc.MatBackwardSolve(self, b, x)

    def solve(self, b, x):
        """
        Solve A x = b

        :Parameters:
          - `b`: the right-hand-side vector.
          - `x`: the solutions vector to store the result.

        .. note:: The vectors `b` and `x` cannot be the same.  I.e.,
           one cannot call ``Solve(x,x)``.

        .. tip:: Most users should employ the simplified KSP interface
           for linear solvers instead of working directly with matrix
           algebra routines such as this.
        """
        _petsc.MatSolve(self, b, x)

    def solveAdd(self, b, y, x):
        """
        Compute x = inv(A)*b + y
        """
        _petsc.MatSolveAdd(self, b, y, x)

    def solveTranspose(self, b, x):
        """
        Solve A' x = b
        """
        _petsc.MatSolveTranspose(self, b, x)

    def solveTransposeAdd(self, b, y, x):
        """
        Compute x = inv(A')*b + y
        """
        _petsc.MatSolveTransposeAdd(self, b, y, x)

    def useScaledForm(self, scaled):
        """
        """
        _petsc.MatUseScaledForm(self, scaled)

    def scaleSystem(self, x=None, b=None):
        """
        """
        _petsc.MatScaleSystem(self, x, b)

    def unScaleSystem(self, x=None, b=None):
        """
        """
        _petsc.MatUnScaleSystem(self, x, b)

    def getShellContext(self):
        """
        Get the user-provided context object associated with a shell
        matrix.
        """
        return _petsc.MatShellGetContext(self)
    
    def setShellContext(self, context):
        """
        Set the user-provided context object associated with a shell
        matrix.
        """
        _petsc.MatShellSetContext(self, context)

    option = property(fset=setOption,
                      doc='Set an option or sequence of options')
    sizes  = property(getSizes, setSizes)

    size   = property(getSize)
    lsize = local_size  = property(getLocalSize)
    gsize = global_size = property(getSize)
    bsize = block_size  = property(getBlockSize, setBlockSize)
    range = owner_range = property(getOwnershipRange)

    assembled  = property(isAssembled)
    symmetric  = property(isSymmetric)
    hermitian  = property(isHermitian)
    structsymm = property(isStructurallySymmetric)


# --------------------------------------------------------------------



class MatSeqDense(Mat):

    """
    Sequential dense matrix that is stored in column major order (the
    usual Fortran 77 manner). Many of the matrix operations use the
    BLAS and LAPACK routines.
    """

    def __init__(self, *targs, **kwargs):
        """
        Create a sequential dense matrix
        
        :Parameters:
          - `size`: tuple ``(m,n)`` with number of rows and columns.
          - `data`: optional location of matrix data.  Set data to
            ``None`` for PETSc to control all matrix memory
            allocation.
          - `comm`: MPI communicator, set to COMM_SELF.
        """
        super(MatSeqDense, self).__init__(*targs, **kwargs)
        self.createSeqDense(*targs, **kwargs)



## class MatSeqBDiag(Mat):

##     """
##     Sparse sequential block diagonal matrix.
##     """

##     def __init__(self,
##                  lsize=None,bsize=None,
##                  diags = None,
##                  comm=None,
##                  *targs, **kwargs):
##     """
##     """
            
    
class MatSeqAIJ(Mat):

    """
    Sequential sparse matrix in AIJ (compressed row) format.

   .. note:: The AIJ format (also called the Yale sparse matrix format
      or compressed row storage), is fully compatible with standard
      Fortran 77 storage.  That is, the stored row and column indices
      can begin at either one (as in Fortran) or zero.  See the PETSc
      users' manual for details.

      For good matrix assembly performance the user should preallocate
      the matrix storage, performance during matrix assembly can be
      increased by more than a factor of 50. For large problems you
      MUST preallocate memory or you will get TERRIBLE performance,
      see the PETSc users' manual chapter on matrices.

      By default, this format uses inodes (identical nodes) when
      possible, to improve numerical efficiency of matrix-vector
      products and solves. We search for consecutive rows with the
      same nonzero structure, thereby reusing matrix information to
      achieve increased efficiency.
    """

    def __init__(self, *targs, **kwargs):
        """
        Create a sparse matrix in AIJ (compressed row) format.

        :Parameters:
          - `size`: tuple ``(rows, cols)`` with number of rows ans
            columns.
          - `nz`: number of nonzeros per row (same for all rows), or
            array containing the number of nonzeros in the various
            rows (possibly different for each row) or ``None``.
          - `comm`: MPI communicator, defaults to `COMM_SELF`.

        .. note:: Specify the preallocated storage with `nz`. Set `nz`
           to `DEFAULT` or ``None`` for PETSc to control dynamic
           memory allocation.
        """
        super(MatSeqAIJ, self).__init__(*targs, **kwargs)
        self.createSeqAIJ(*targs, **kwargs)


class MatSeqBAIJ(Mat):

    """
    Sequential sparse matrix in block AIJ format.
    """

    def __init__(self, *targs, **kwargs):
        """
        """
        super(MatSeqBAIJ, self).__init__(*targs, **kwargs)
        self.createSeqAIJ(*targs, **kwargs)


class MatSeqSBAIJ(Mat):

    """
    Sequential symmetric sparse matrix in block AIJ format.
    """

    def __init__(self, *targs, **kwargs):
        """
        """
        super(MatSeqSBAIJ, self).__init__(*targs, **kwargs)
        self.createSeqSBAIJ(*targs, **kwargs)



class MatMPIDense(Mat):

    """
    Parallel dense matrix which is fully compatible with standard
    Fortran 77 storage by columns.
    """

    def __init__(self, *targs, **kwargs):
        """
        Creates a parallel matrix in dense format,

        :Parameters:
          - `lsize`: tuple ``(m,n)`` with global number of rows and
            columns (or `DECIDE` to have calculated if `gsize` is
            given).
          - `gsize`: tuple ``(M,N)`` with global number of rows and
            columns (or `DECIDE` to have calculated if `lsize` is
            given).
          - `data`: optional location of matrix data.  Set data to
            ``None`` for PETSc to control all matrix memory
            allocation.
          - `comm`: MPI communicator.
        """
        super(MatMPIDense, self).__init__(*targs, **kwargs)
        self.createMPIDense(*targs, **kwargs)
    

## class MatMPIBDiag(Mat):

##     """
##     Sparse parallel block diagonal matrix.
##     """

##     def __init__(self,
##                  lsize=None,gsize=None,bsize=None,
##                  diags = None,
##                  comm=None,
##                  *targs, **kwargs):
##     """
##     """


 
class MatMPIAIJ(Mat):

    """
    Parallel sparse matrix in AIJ (compressed row) format.
    
    Consider the following 8x8 matrix with 34 non-zero values, that is
    assembled across 3 processors. Lets assume that proc0 owns 3 rows,
    proc1 owns 3 rows, proc2 owns 2 rows. This division can be shown
    as follows::

        -------------------------------------
                1  2  0  |  0  3  0  |  0  4
        Proc0   0  5  6  |  7  0  0  |  8  0
                9  0 10  | 11  0  0  | 12  0
        -------------------------------------
               13  0 14  | 15 16 17  |  0  0
        Proc1   0 18  0  | 19 20 21  |  0  0 
                0  0  0  | 22 23  0  | 24  0
        -------------------------------------
        Proc2  25 26 27  |  0  0 28  | 29  0
               30  0  0  | 31 32 33  |  0 34
        -------------------------------------
        
    This can be represented as a collection of submatrices as::

        A B C
        D E F
        G H I

    Where the submatrices A,B,C are owned by proc0, D,E,F are
    owned by proc1, G,H,I are owned by proc2.

    The ``m`` parameters for proc0,proc1,proc2 are 3,3,2
    respectively.  The ``n`` parameters for proc0,proc1,proc2 are 3,3,2
    respectively.  The `M`,`N` parameters are 8,8, and have the same
    values on all procs.

    The DIAGONAL submatrices corresponding to proc0,proc1,proc2 are
    submatrices ``[A]``, ``[E]``, ``[I]`` respectively. The
    OFF-DIAGONAL submatrices corresponding to proc0,proc1,proc2 are
    ``[BC]``, ``[DF]``, ``[GH]`` respectively.  Internally, each
    processor stores the DIAGONAL part, and the OFF-DIAGONAL part as
    `SeqAIJ` matrices. for eg: proc1 will store ``[E]`` as a SeqAIJ
    matrix, ans ``[DF]`` as another `SeqAIJ` matrix.

    When `d_nz`, `o_nz` parameters are specified, `d_nz` storage
    elements are allocated for every row of the local diagonal
    submatrix, and `o_nz` storage locations are allocated for every
    row of the OFF-DIAGONAL submat.  One way to choose `d_nz` and
    `o_nz` is to use the max nonzerors per local rows for each of the
    local DIAGONAL, and the OFF-DIAGONAL submatrices.  In this case,
    the values of `d_nz`,`o_nz` are::

        proc0 : dnz = 2, o_nz = 2
	proc1 : dnz = 3, o_nz = 2
	proc2 : dnz = 1, o_nz = 4

    We are allocating ``m*(d_nz+o_nz)`` storage locations for every
    proc. This translates to ``3*(2+2)=12`` for proc0, ``3*(3+2)=15``
    for proc1, ``2*(1+4)=10`` for proc3. i.e we are using
    ``12+15+10=37`` storage locations to store 34 values.

    When `d_nnz`, `o_nnz` parameters are specified, the storage is
    specified for every row, coresponding to both DIAGONAL and
    OFF-DIAGONAL submatrices.  In the above case the values for
    `d_nnz`,`o_nnz` are::

        proc0: d_nnz = [2,2,2] and o_nnz = [2,2,2]
	proc1: d_nnz = [3,3,2] and o_nnz = [2,1,1]
	proc2: d_nnz = [1,1]   and o_nnz = [4,4]

    Here the space allocated is sum of all the above values i.e 34, and
    hence pre-allocation is perfect.
    """

    def __init__(self, *targs, **kwargs):
        """
        Create a sparse parallel matrix in AIJ format (the default
        parallel PETSc format).  For good matrix assembly performance
        the user should preallocate the matrix storage by setting the
        parameters d_nz (or d_nnz) and o_nz (or o_nnz).  By setting
        these parameters accurately, performance can be increased by
        more than a factor of 50.

        :Parameters:
          - `lsize`: tuple ``(m,n)`` with number of local rows ``m``
            and columns ``n`` (or `DECIDE` to have calculated if
            `gsize` is given). This value should be the same as the
            local size used in creating the y vector for the
            matrix-vector product y = Ax. For square matrices ``m``
            is almost always ``n``.
          - `gsize`: tuple ``(M,N)`` with number of global rows ``M``
            and columns ``N`` (or `DETERMINE` to have calculated if
            `lsize` is given). For square matrices ``M`` is almost
            always ``N``.
          - `d_nz`: number of nonzeros per row in DIAGONAL portion of
            local submatrix (same value is used for all local rows).
          - `d_nnz`: array containing the number of nonzeros in the
            various rows of the DIAGONAL portion of the local
            submatrix (possibly different for each row) or ``None``,
            if `d_nz` is used to specify the nonzero structure. The
            size of this array is equal to the number of local rows,
            i.e ``m``. You must leave room for the diagonal entry
            even if it is zero.
          - `o_nz`: number of nonzeros per row in the OFF-DIAGONAL
            portion of local submatrix (same value is used for all
            local rows).
          - `o_nnz`: array containing the number of nonzeros in the
            various rows of the OFF-DIAGONAL portion of the local
            submatrix (possibly different for each row) or ``None``,
            if `o_nz` is used to specify the nonzero structure. The
            size of this array is equal to the number of local rows,
            i.e ``m``.
          - `csr`: sequence ``(i,j)`` or ``(i,j,v)`` providing arrays
            for indices and values in CSR format.
          - `comm`: MPI communicator.
        """
        super(MatMPIAIJ, self).__init__(*targs, **kwargs)
        self.createMPIAIJ(*targs, **kwargs)


class MatMPIBAIJ(Mat):

    """
    Parallel sparse matrix in block AIJ format.
    """

    def __init__(self, *targs, **kwargs):
        """See `Mat.createMPIBAIJ()`"""
        super(MatMPIBAIJ, self).__init__(*targs, **kwargs)
        self.createMPIAIJ(*targs, **kwargs)


class MatMPISBAIJ(Mat):

    """
    Parallel symmetric sparse matrix in block AIJ format.
    """

    def __init__(self, *targs, **kwargs):
        """See `Mat.createMPISBAIJ()`"""
        super(MatMPISBAIJ, self).__init__(*targs, **kwargs)
        self.createMPISBAIJ(*targs, **kwargs)
        

class MatIS(Mat):

    """
    A matrix type to be used for using the Neumann-Neumann type
    preconditioners.

    This format stores the matrices in globally unassembled form. Each
    processor assembles only its local Neumann problem and the
    parallel matrix vector product is handled *implicitly*
    """

    def __init__(self, *targs, **kwargs):
        """See `Mat.createIS()`"""
        super(MatIS, self).__init__(*targs, **kwargs)
        self.createIS(*targs, **kwargs)

    def getLocalMat(self):
        """
        Get the local matrix stored inside a IS matrix.

        .. note:: This can be called if you have precomputed the
           nonzero structure of the local matrix and want to provide
           it to the inner matrix object to improve the performance of
           the `setValues()` operation.
        """
        return _petsc.MatISGetLocalMat(self)

# --------------------------------------------------------------------


class MatScatter(Mat):

    """
    Matrix based on a Scatter.
    """

    def __init__(self, *targs, **kwargs):
        """See `Mat.createScatter()`"""
        super(MatScatter, self).__init__(*targs, **kwargs)
        self.createScatter(*targs, **kwargs)


# --------------------------------------------------------------------


class MatNormal(Mat):

    """
    Matrix that behaves like A'*A.
    """

    def __init__(self, *targs, **kwargs):
        """See `Mat.createNormal()`"""
        super(MatNormal, self).__init__(*targs, **kwargs)
        self.createNormal(*targs, **kwargs)


# --------------------------------------------------------------------


class MatShell(Mat):

    """
    A matrix type to be used to define your own matrix type (perhaps
    matrix free).
    """

    def __init__(self, *targs, **kwargs):
        """See `Mat.createShell()`."""
        super(MatShell, self).__init__(*targs, **kwargs)
        self.createShell(*targs, **kwargs)

        
# --------------------------------------------------------------------


class NullSpace(Object):

    """
    Data structure used to project vectors out of null spaces.
    """

    def __init__(self, *targs, **kwargs):
        """See `create()`"""
        super(NullSpace, self).__init__(*targs, **kwargs)
        if targs or kwargs:
            self.create(*targs, **kwargs)

    def __call__(self, vec, out=None):
        """Same as `remove()`."""
        _petsc.MatNullSpaceRemove(self, vec, out)

    def create(self, vecs=None, has_const=False, comm=None):
        """
        Create a data structure used to project vectors out of null
        spaces.

        :Parameters:
          - `vecs`: sequence with vectors that span the null space
            (excluding the constant vector); these vectors must be
            orthonormal. These vectors are NOT copied, so do not
            change them after this call.
          - `has_const`: 'True' if the null space contains the
            constant vector; otherwise 'False' (default).
          - `comm`: MPI communicator (defaults to COMM_WORLD).
        """
        return _petsc.MatNullSpaceCreate(comm, has_const, vecs, self)
        
    def remove(self, vec, out=None):
        """
        Remove all the components of a null space from a vector.
        
        :Parameters:
          - `vec`: the vector from which the null space is to be
            removed.
          - `out`: the vector to store the result. If `out` is
            ``None``, the null space removal is done in-place in `vec`
        """
        _petsc.MatNullSpaceRemove(self, vec, out)


    def test(self, mat):
        """
        Test if the claimed null space is really a null space of a
        matrix
        """
        _petsc.MatNullSpaceTest(self, mat)


# --------------------------------------------------------------------
