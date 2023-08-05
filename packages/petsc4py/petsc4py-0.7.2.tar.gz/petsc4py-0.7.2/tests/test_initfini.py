import unittest
from petsc4py import PETSc

# --------------------------------------------------------------------

class TestInitFini(unittest.TestCase):
    
    def testInitFini(self):
        self.assertTrue(PETSc.IsInitialized())
        self.assertFalse(PETSc.IsFinalized())
        PETSc.Initialize()
        PETSc.Initialize()
        self.assertTrue(PETSc.IsInitialized())
        self.assertFalse(PETSc.IsFinalized())
        PETSc.Finalize()
        PETSc.Finalize()
        self.assertFalse(PETSc.IsInitialized())
        self.assertTrue(PETSc.IsFinalized())
        self.assertRaises(RuntimeError, PETSc.Initialize)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
