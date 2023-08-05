import sys
from petsc import Initialize
Initialize(sys.argv)

import petsc.PETSc as PETSc
import scipy.base  as array
from time import time

def test_assemble(loops, size, options):
    # elemental matrices
    z = array.zeros((size, size), dtype=PETSc.Scalar)
    o = array.ones((size, size), dtype=PETSc.Scalar)
    i = array.arange(size, dtype=PETSc.Int)
    j = array.arange(size, dtype=PETSc.Int)
    im = PETSc.InsertMode.ADD_VALUES
    # global matrix
    A = PETSc.Mat.CreateSeqAIJ(size, nz=size)
    for opt in options:
        A.setOption(opt)
    # pre assembly
    A_setValues = A.setValues
    A_setValues(i, j, o, im)
    #
    mi, mj = -i, -j
    tm = time()
    for k in xrange(loops):
        A_setValues(mi, mj, o, im)
    A.assemble()
    tm = time() - tm
    tm /= loops
    # 
    tz = time()
    for k in xrange(loops):
        A_setValues(i, j, z, im)
    A.assemble()
    tz = time() - tz
    tz /= loops
    #
    A_setValues = A.setValues
    to = time()
    for k in xrange(loops):
        A_setValues(i, j, o, im)
    A.assemble()
    to = time() - to
    to /= loops
    
    return tm, tz, to,  A

# ---

def test():

    L     = [3000, 1000, 500, 500, 100,  10,    5,    2]
    sizes = [   2,    5,  10,  50, 100, 500, 1000, 3000]

    template = 'tm: %f, tz: %f, to: %f, tm/to: %f, tz/to: %f'
    
    for i, N in enumerate(sizes):
        print '-' * 70
        print 'Matrix Size: (%d, %d)' % (N, N)
        print '-' * 70
        ## ----
        opts = []
        tm, tz, to, A = test_assemble(L[i], N, opts)
        del A
        print 'opts = []'
        print template % (tm, tz, to, tm/to, tz/to)

        ## ----
        opts += [PETSc.Mat.Option.DO_NOT_USE_INODES]
        tm, tz, to, A = test_assemble(L[i], N, opts)
        del A
        print 'opts += [MAT_DO_NOT_USE_INODES]'
        print template % (tm, tz, to, tm/to, tz/to)

        ## ----
        opts += [PETSc.Mat.Option.IGNORE_ZERO_ENTRIES]
        tm, tz, to, A = test_assemble(L[i], N, opts)
        del A
        print 'opts += [MAT_IGNORE_ZERO_ENTRIES]'
        print template % (tm, tz, to, tm/to, tz/to)



if __name__ == '__main__':
    test()
