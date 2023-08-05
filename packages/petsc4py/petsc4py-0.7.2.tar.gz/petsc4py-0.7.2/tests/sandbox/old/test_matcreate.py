from  petsc import PETSc
import unittest


class MatCreate(unittest.TestCase):

    def testCreate(self):
        #
        A = PETSc.Mat.Create(size=0)
        #
        A = PETSc.Mat.Create(size=(0,0), nz=0)
        #
        A = PETSc.Mat.Create(size=(0,0), nz=[])

        assert A.getSize() == (0,0)
        if PETSc.WORLD_SIZE == 1:
            assert A.getType() == PETSc.Mat.Type.SEQAIJ
        else:
            assert A.getType() == PETSc.Mat.Type.MPIAIJ
        #
        A = PETSc.Mat.Create(size=(0,0), bsize=2, nz=2)
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
        A = PETSc.Mat.CreateSeqAIJ(0, bsize=1)
        A = PETSc.Mat.CreateSeqAIJ(0, nz=0)
        A = PETSc.Mat.CreateSeqAIJ(0, nz=PETSc.DECIDE)
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
            inz  = size[1]//bs
            anz = xrange(size[0]//bs)
            A = PETSc.Mat.CreateSeqAIJ(0,    bsize=bs)
            A = PETSc.Mat.CreateSeqAIJ(size, bsize=bs, nz=inz)
            A = PETSc.Mat.CreateSeqAIJ(size, bsize=bs, nz=anz)
            assert A.getSize() == size
            assert A.getBlockSize() == bs
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
        A = PETSc.Mat.CreateMPIAIJ((lsize, gsize), csr=(i, j))
        A = PETSc.Mat.CreateMPIAIJ((lsize, gsize), csr=(i, j, v))

        gsize  = None
        lsizes = [(6, 12), (12, 24), (18, 36)]
        bsizes = [2, 3]
        for lsize in lsizes:
            for bs in bsizes:
                mbs, nbs = (sz//bs for sz in lsize)
                i = range(0, (mbs*nbs)+1, nbs)
                j = range(nbs) * mbs
                A = PETSc.Mat.CreateMPIAIJ((lsize, gsize), bs, csr=(i, j))
                v = [(k-(nbs*mbs*bs)//2) for k in xrange(nbs*mbs*bs)]
                v = [-10 for k in xrange(nbs*mbs*bs)]
                A = PETSc.Mat.CreateMPIAIJ((lsize, gsize), bs, csr=(i, j, v))
                assert A.getBlockSize() == bs
                assert A.getType() == PETSc.Mat.Type.MPIBAIJ

if __name__ == '__main__':
    unittest.main()
