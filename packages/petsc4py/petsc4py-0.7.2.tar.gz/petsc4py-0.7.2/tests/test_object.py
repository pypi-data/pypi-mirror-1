from petsc4py import PETSc
import unittest

# --------------------------------------------------------------------

class TestObjectBase(object):

    CLASS, TARGS, KARGS = None, [], {}
    BUILD = None
    def setUp(self):
        self.obj = self.CLASS(*self.TARGS, **self.KARGS)
        if not self.obj:
            self.obj.create()
        #print self.obj.klass, self.obj.type

    def tearDown(self):
        self.obj = None

    def testClass(self):
        self.assertTrue(isinstance(self.obj, self.CLASS))
        self.assertTrue(type(self.obj) is self.CLASS)
    
    def testNonZero(self):
        self.assertTrue(bool(self.obj))
        
    def testDestroy(self):
        this = self.obj.this
        self.assertTrue(self.obj.this is this)
        self.obj.destroy()
        self.assertFalse(bool(self.obj))
        self.assertRaises(PETSc.Error, self.obj.destroy)
        self.assertTrue(self.obj.this is this)

    def testOptions(self):
        self.assertEqual(self.obj.getOptionsPrefix(), '')
        prefix1 = 'my_'
        self.obj.setOptionsPrefix(prefix1)
        self.assertEqual(self.obj.getOptionsPrefix(), prefix1)
        prefix2 = 'opt_'
        self.obj.setOptionsPrefix(prefix2)
        self.assertEqual(self.obj.getOptionsPrefix(), prefix2)
        self.obj.appendOptionsPrefix(prefix1)
        self.assertEqual(self.obj.getOptionsPrefix(),
                         prefix2 + prefix1)
        self.obj.prependOptionsPrefix(prefix1)
        self.assertEqual(self.obj.getOptionsPrefix(),
                         prefix1 + prefix2 + prefix1)
        self.obj.setFromOptions()

    def testName(self):
        oldname = self.obj.getName()
        newname = '%s-%s' %(oldname, oldname)
        self.obj.setName(newname)
        self.assertEqual(self.obj.getName(), newname)
        self.obj.setName(oldname)
        self.assertEqual(self.obj.getName(), oldname)

    def testRefCount(self):
        self.assertEqual(self.obj.getRefCount(), 1)
        self.obj.addReference()
        self.assertEqual(self.obj.getRefCount(), 2)
        self.obj.addReference()
        self.assertEqual(self.obj.getRefCount(), 3)
        self.obj.delReference()
        self.assertEqual(self.obj.getRefCount(), 2)
        self.obj.delReference()
        self.assertEqual(self.obj.getRefCount(), 1)
        self.obj.delReference()
        self.assertFalse(bool(self.obj))
        
    def testState(self):
        state = self.obj.getState()
        self.obj.increaseState()
        self.assertEqual(self.obj.getState(), state + 1)
        self.obj.increaseState()
        self.assertEqual(self.obj.getState(), state + 2)
        self.obj.setState(state + 3)
        self.assertEqual(self.obj.getState(), state + 3)
        self.obj.increaseState()
        self.assertEqual(self.obj.getState(), state + 4)
        self.obj.decreaseState()
        self.assertEqual(self.obj.getState(), state + 3)

    def testComposeQuery(self):
        self.obj.compose('myobj', self.obj)
        self.assertEqual(self.obj.query('myobj'), self.obj)
        self.assertEqual(self.obj.getRefCount(), 2)
        self.obj.compose('myobj', None)
        self.assertEqual(self.obj.getRefCount(), 1)
        self.assertEqual(self.obj.query('myobj'), None)

    def testComm(self):
        comm = self.obj.getComm()
        self.assertTrue(isinstance(comm, PETSc.Comm))
        self.assertTrue(comm in [PETSc.COMM_SELF, PETSc.COMM_WORLD])

    def testProperties(self):
        self.assertEqual(self.obj.getCookie(),    self.obj.cookie)
        self.assertEqual(self.obj.getClassName(), self.obj.klass)
        self.assertEqual(self.obj.getType(),      self.obj.type)
        self.assertEqual(self.obj.getName(),      self.obj.name)
        self.assertEqual(self.obj.getState(),     self.obj.state)
        self.assertEqual(self.obj.getComm(),      self.obj.comm)
        self.assertEqual(self.obj.getRefCount(),  self.obj.refcount)
        self.assertNotEqual(self.obj.this,  None)
        self.assertTrue(self.obj.this is self.obj.this)
        self.assertTrue(self.obj.thisown)
        
# --------------------------------------------------------------------

class TestObjectRandom(TestObjectBase, unittest.TestCase):
    CLASS = PETSc.Random

class TestObjectViewerASCII(TestObjectBase, unittest.TestCase):
    CLASS = PETSc.ViewerASCII
    TARGS = ('stdout',)

class TestObjectViewerBinary(TestObjectBase, unittest.TestCase):
    CLASS = PETSc.ViewerBinary

## class TestObjectViewerDraw(TestObjectBase, unittest.TestCase):
##     CLASS = PETSc.ViewerDraw

class TestObjectIS(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.ISGeneral
    TARGS = ([],)

class TestObjectLGMapping(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.LGMapping
    TARGS = ([],)

class TestObjectAO(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.AOMapping
    TARGS = ([], [])
    

class TestObjectVec(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.VecSeq
    TARGS = (0,)

class TestObjectScatter(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.Scatter
    def setUp(self):
        v1, v2 = PETSc.Vec().createSeq(0), PETSc.Vec().createSeq(0)
        i1, i2 = PETSc.ISGeneral([]), PETSc.ISGeneral([])
        self.obj = PETSc.Scatter(v1, i1, v2, i2)
        del v1, v2, i1, i2

class TestObjectMat(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.MatSeqAIJ
    TARGS = (0,)

class TestObjectNullSpace(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.NullSpace
    TARGS = ([], True)

class TestObjectKSP(TestObjectBase, unittest.TestCase):
    CLASS = PETSc.KSP

class TestObjectPC(TestObjectBase, unittest.TestCase):
    CLASS = PETSc.PC

class TestObjectSNES(TestObjectBase, unittest.TestCase):
    CLASS = PETSc.SNES

class TestObjectTS(TestObjectBase, unittest.TestCase):
    CLASS  = PETSc.TS
    TARGS = ('nonlinear', 'beuler')
    def setUp(self):
        self.obj = self.CLASS(*self.TARGS, **self.KARGS)
        self.obj.create()
        self.obj.setProblemType(self.TARGS[0])
        self.obj.setType(self.TARGS[1])

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
