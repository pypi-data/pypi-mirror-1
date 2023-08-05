import sys
import unittest
import petsc.PETSc as PETSc

__all__ = ['MatCreate',
           'MatMatMult']

if '-v' in sys.argv or '--verbose' in sys.argv:
    verbose = True
else:
    verbose = False

verbose = False


class MatCreate(unittest.TestCase):

    def testCreate(self):
        #
        A = PETSc.Mat.Create(size=0)
        #
        A = PETSc.Mat.Create(size=0, nz=[])
        assert A.getSize() == (0,0)
        if PETSc.WORLD_SIZE == 1:
            assert A.getType() == PETSc.Mat.Type.SEQAIJ
        else:
            assert A.getType() == PETSc.Mat.Type.MPIAIJ
        #
        A = PETSc.Mat.Create(size=0, bsize=2, nz=2)
        assert A.getBlockSize() == 2
        if PETSc.WORLD_SIZE == 1:
            assert A.getType() == PETSc.Mat.Type.SEQBAIJ
        else:
            assert A.getType() == PETSc.Mat.Type.MPIBAIJ

    def testCreateSeqAIJ(self):
        #
        COMM = PETSc.COMM_WORLD
        try:
            A = PETSc.Mat.CreateSeqAIJ(0, comm=COMM)
        except ValueError:
            pass
            #print 'PETSc.Mat.CreateSeqAIJ() ' \
            #      'called with invalid comm'
        DECIDE = PETSc.DECIDE
        for size in [DECIDE, (0, DECIDE), (DECIDE, 0), (DECIDE, DECIDE)]:
            try:
                A = PETSc.Mat.CreateSeqAIJ(size)
            except ValueError:
                pass
                #print 'Mat.CreateSeqAIJ() ' \
                #      'called with invalid size %s' % (size,)
        #
        A = PETSc.Mat.CreateSeqAIJ(0)
        A = PETSc.Mat.CreateSeqAIJ(0,nz=0)
        A = PETSc.Mat.CreateSeqAIJ(0, nz=[])
        assert A.getSize() == (0,0)
        assert A.getType() == PETSc.Mat.Type.SEQAIJ
        #
        A = PETSc.Mat.CreateSeqAIJ(2)
        A = PETSc.Mat.CreateSeqAIJ(2, nz=2)
        A = PETSc.Mat.CreateSeqAIJ(2, nz=[1,2])
        assert A.getSize() == (2, 2)
        assert A.getType() == PETSc.Mat.Type.SEQAIJ
        #
        A = PETSc.Mat.CreateSeqAIJ((2, 3))
        A = PETSc.Mat.CreateSeqAIJ((2, 3), nz=3)
        A = PETSc.Mat.CreateSeqAIJ((2, 3), nz=[2,3])
        assert A.getSize() == (2, 3)
        assert A.getType() == PETSc.Mat.Type.SEQAIJ
        #
        size = (12, 24)
        bsize = [2, 3, 4]
        for bs in bsize:
            nz  = size[1]//bs
            nnz = xrange(size[0]//bs)
            A = PETSc.Mat.CreateSeqAIJ(0, bsize=bs)
            A = PETSc.Mat.CreateSeqAIJ(size, bsize=bs, nz=nz)
            A = PETSc.Mat.CreateSeqAIJ(size, bsize=bs, nz=nnz)
            assert A.getSize() == size
            assert A.getType() == PETSc.Mat.Type.SEQBAIJ

    def testCreateAIJCSR(self):
        i = range(0, 21, 3)
        j = [0, 2, 4, 1, 3, 5]*3
        v = [(k+1)*10 for k in xrange(len(j))]

        size = (6, 6)
        A = PETSc.Mat.CreateSeqAIJ(size, csr=(i, j))
        A = PETSc.Mat.CreateSeqAIJ(size, csr=(i, j, v))

        gsize = (PETSc.DECIDE, 6)
        lsize = (6, PETSc.DECIDE)
        A = PETSc.Mat.CreateMPIAIJ([lsize, gsize], csr=(i, j))
        A = PETSc.Mat.CreateMPIAIJ([lsize, gsize], csr=(i, j, v))

        gsize  = None
        lsize = (6, 12)
        bsize = [2, 3]
        for bs in bsize:
            mbs, nbs = (sz//bs for sz in lsize)
            i = range(0, (mbs*nbs)+1, nbs)
            j = range(nbs) * mbs
            A = PETSc.Mat.CreateMPIAIJ([lsize, gsize], bs, csr=(i, j))
            v = [(k-(nbs*mbs*bs)//2) for k in xrange(nbs*mbs*bs)]
            v = [-10 for k in xrange(nbs*mbs*bs)]
            A = PETSc.Mat.CreateMPIAIJ([lsize, gsize], bs, csr=(i, j, v))
            assert A.getType() == PETSc.Mat.Type.MPIBAIJ

class MatMatMult(unittest.TestCase):

    def setUp(self):
        m, n = 3, 5
        self.sizes = m, n
        self.A = PETSc.Mat.CreateSeqAIJ((m, n))
        self.B = PETSc.Mat.CreateSeqAIJ((n, m))
        # Aij = min(i,j); i=1..m, j=1..n
        for i in xrange(m):
            for j in xrange(n):
                self.A[i,j] = min(i,j) + 1
        self.A.assemble()
        # Bij = max(i,j); i=1..m, j=1..n
        for i in xrange(n):
            for j in xrange(m):
                self.B[i,j] = max(i,j) + 1
        self.B.assemble()

    def tearDown(self):
        self.A.destroy()
        self.B.destroy()
        
    def testMatMatMult(self):
        A, B = self.A, self.B
        # C = A * B
        C = A.matMult(B)
        PETSc.Mat.matMult(A, B, C)
        # D = B * A
        D = B.matMultSymbolic(A)
        PETSc.Mat.matMultNumeric(B, A, D)
        #
        if verbose:
            for name, matrix in [('A',        A),
                                 ('B',        B),
                                 ('C (=A*B)', D),
                                 ('D (=B*A)', D)]:
                print name,':'
                matrix.view()
                print

if __name__ == '__main__':
    unittest.main()
