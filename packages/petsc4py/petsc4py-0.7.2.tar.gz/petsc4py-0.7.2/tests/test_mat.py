from petsc4py import PETSc
import unittest

# --------------------------------------------------------------------

class TestMatCreate(unittest.TestCase):

    def testCreateDefault(self):
        aijtypes = [PETSc.Mat.Type.AIJ,
                    PETSc.Mat.Type.SEQAIJ,
                    PETSc.Mat.Type.MPIAIJ]
        A = PETSc.Mat().create(); A.setSizes(0)
        A.setFromOptions()
        A = PETSc.Mat().create(); A.setSizes([0,0])
        self.assertEqual(A.getSize(), (0,0))
        self.assertEqual(A.getType(), '')
        A.setFromOptions()
        self.assertTrue(A.getType() in aijtypes)
        A = PETSc.Mat().create()
        self.assertEqual(A.getType(), '')
        A.setSizes((0,0))
        self.assertEqual(A.getSize(), (0,0))
        A.setFromOptions()
        self.assertTrue(A.getType() in aijtypes)
        A.setBlockSize(2)
        self.assertEqual(A.getBlockSize(), 2)

    def testCreateSeqAIJ(self):
        try:
            A = PETSc.Mat().createSeqAIJ(0, comm=PETSc.COMM_WORLD)
        except ValueError:
            pass
        DECIDE = PETSc.DECIDE
        for size in [DECIDE, (0, DECIDE), (DECIDE, 0), (DECIDE, DECIDE)]:
            try:
                A = PETSc.Mat().createSeqAIJ(size)
            except ValueError:
                pass
                #print 'Mat.CreateSeqAIJ() ' \
                #      'called with invalid size %s' % (size,)
        #
        A = PETSc.Mat().createSeqAIJ(0, bsize=1)
        A = PETSc.Mat().createSeqAIJ(0, nz=0)
        A = PETSc.Mat().createSeqAIJ(0, nz=PETSc.DECIDE)
        self.assertEqual(A.getSize(), (0,0))
        self.assertEqual(A.getType(), PETSc.Mat.Type.SEQAIJ)
        #
        A = PETSc.Mat().createSeqAIJ(2)
        A = PETSc.Mat().createSeqAIJ(2, nz=2)
        A = PETSc.Mat().createSeqAIJ(2, nz=[1,2])
        self.assertEqual(A.getSize(), (2, 2))
        self.assertEqual(A.getType(), PETSc.Mat.Type.SEQAIJ)
        #
        A = PETSc.Mat().createSeqAIJ((2, 3))
        A = PETSc.Mat().createSeqAIJ((2, 3), nz=3)
        A = PETSc.Mat().createSeqAIJ((2, 3), nz=[2,3])
        self.assertEqual(A.getSize(), (2, 3))
        self.assertEqual(A.getType(), PETSc.Mat.Type.SEQAIJ)
        #
        size = (12, 24)
        bsize = [2, 3, 4]
        for bs in bsize:
            inz  = size[1]//bs
            anz = xrange(size[0]//bs)
            A = PETSc.Mat().createSeqAIJ(0,    bsize=bs)
            A = PETSc.Mat().createSeqAIJ(size, bsize=bs, nz=inz)
            A = PETSc.Mat().createSeqAIJ(size, bsize=bs, nz=anz)
            self.assertEqual(A.getSize(), size)
            self.assertEqual(A.getBlockSize(), bs)
            self.assertEqual(A.getType(), PETSc.Mat.Type.SEQBAIJ)

    def testCreateAIJCSR(self):
        i = range(0, 21, 3)
        j = [0, 2, 4, 1, 3, 5]*3
        v = [(k+1)*10 for k in xrange(len(j))]

        size = (6, 6)
        A = PETSc.Mat().createSeqAIJ(size, csr=(i, j))
        A = PETSc.Mat().createSeqAIJ(size, csr=(i, j, v))

        gsize = (PETSc.DECIDE, 6)
        lsize = (6, PETSc.DECIDE)
        A = PETSc.Mat().createMPIAIJ((lsize, gsize), csr=(i, j))
        A = PETSc.Mat().createMPIAIJ((lsize, gsize), csr=(i, j, v))

        gsize  = None
        lsizes = [(6, 12), (12, 24), (18, 36)]
        bsizes = [2, 3]
        for lsize in lsizes:
            for bs in bsizes:
                mbs, nbs = (sz//bs for sz in lsize)
                i = range(0, (mbs*nbs)+1, nbs)
                j = range(nbs) * mbs
                A = PETSc.Mat().createMPIAIJ((lsize, gsize), bs, csr=(i, j))
                v = [(k-(nbs*mbs*bs)//2) for k in xrange(nbs*mbs*bs)]
                v = [-10 for k in xrange(nbs*mbs*bs**2)]
                A = PETSc.Mat().createMPIAIJ((lsize, gsize), bs, csr=(i, j, v))
                self.assertEqual(A.getBlockSize(), bs)
                self.assertEqual(A.getType(), PETSc.Mat.Type.MPIBAIJ)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
