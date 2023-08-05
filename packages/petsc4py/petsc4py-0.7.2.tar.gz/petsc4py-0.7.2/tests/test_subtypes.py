from petsc4py import PETSc
import unittest

# --------------------------------------------------------------------

class TestSubTypes(unittest.TestCase):

    def testRandom(self):
        self._testCls(PETSc.Random)
    def testKSP(self):
        self._testCls(PETSc.KSP)
    def testPC(self):
        self._testCls(PETSc.PC)
    def testSNES(self):
        self._testCls(PETSc.SNES)
    def testTS(self):
        self._testCls(PETSc.TS)
        
    def _testCls(self, klass):
        for cls in klass.__subclasses__():
            try:
                obj1 = cls()
            except PETSc.Error, e:
                if 'Unknown type' in e[1]:
                    return
            self.assertEqual(obj1.type, cls.TYPE)
            self.assertEqual(obj1.getRefCount(), 1)
            obj2 = cls(obj1)
            self.assertEqual(obj1, obj2)
            self.assertEqual(obj1.getRefCount(), 2)
            del obj2
            self.assertEqual(obj1.getRefCount(), 1)
            obj1 = cls(PETSc.COMM_SELF)
            self.assertEqual(obj1.type, cls.TYPE)
            

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
