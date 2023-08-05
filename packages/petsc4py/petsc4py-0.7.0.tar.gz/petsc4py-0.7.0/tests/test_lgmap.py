from petsc4py import PETSc
import unittest

# --------------------------------------------------------------------

class TestLGMappingBase(object):

    def tearDown(self):
        self.lgmap = None

    def testGetSize(self):
        size = self.lgmap.getSize()
        self.assertTrue(size >=0)
       
    def testGetInfo(self):
        info = self.lgmap.getInfo()
        if self.lgmap.getComm().getSize() == 1:
            self.assertEqual(info, {})
        else:
            self.assertEqual(type(info), dict)

    def testApply(self):
        idxin  = list(range(self.lgmap.getSize()))
        idxout = self.lgmap.apply(idxin)
        self.lgmap.apply(idxin, idxout)

    def testApplyIS(self):
        is_in  = PETSc.ISStride(self.lgmap.getSize())
        is_out = self.lgmap.apply(is_in)
        
    def testProperties(self):
        for prop in ('size', 'info'):
            self.assertTrue(hasattr(self.lgmap, prop))

# --------------------------------------------------------------------

class TestLGMapping(TestLGMappingBase, unittest.TestCase):

    def setUp(self):
        comm_size = PETSc.COMM_WORLD.getSize()
        comm_rank = PETSc.COMM_WORLD.getRank()
        lsize = 10
        first = lsize * comm_rank
        last  = first + lsize
        self.idx   = list(range(first, last))
        self.lgmap = PETSc.LGMapping(self.idx)

class TestLGMappingIS(TestLGMappingBase, unittest.TestCase):

    def setUp(self):
        comm_size = PETSc.COMM_WORLD.getSize()
        comm_rank = PETSc.COMM_WORLD.getRank()
        lsize = 10
        first = lsize * comm_rank
        last  = first + lsize
        self.idx   = list(range(first, last))
        self.iset  = PETSc.ISGeneral(self.idx)
        self.lgmap = PETSc.LGMapping(self.iset)

    def testSameComm(self):
        comm1 = self.lgmap.getComm()
        comm2 = self.iset.getComm()
        self.assertEqual(comm1, comm2)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
