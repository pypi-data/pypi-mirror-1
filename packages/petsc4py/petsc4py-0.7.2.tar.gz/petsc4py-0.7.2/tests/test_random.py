from petsc4py import PETSc
import unittest

# --------------------------------------------------------------------

class TestRandomBase(object):

    RANDOM_TYPE = None

    def setUp(self):
        self.rnd = PETSc.Random()
        self.rnd.create()
        if self.RANDOM_TYPE:
            self.rnd.setType(self.RANDOM_TYPE)

    def tearDown(self):
        self.rnd = None

    def testGetType(self):
        self.assertEqual(self.RANDOM_TYPE, self.rnd.getType())
        self.assertEqual(self.RANDOM_TYPE, self.rnd.type)

    def testSetType(self):
        self.rnd.setType(self.rnd.getType())

    def testCall(self):
        rndval = self.rnd()
        self.assertTrue(isinstance(rndval, (int, float, complex)))
        
    def testGetValue(self):
        rndval = self.rnd.getValue()
        self.assertTrue(isinstance(rndval, (int, float, complex)))
        rndval = self.rnd.getValueReal()
        self.assertTrue(isinstance(rndval, (int, float, complex)))
        rndval = self.rnd.getValueImaginary()
        self.assertTrue(isinstance(rndval, (int, float, complex)))

    def testGetSetInterval(self):
        v = self.rnd.getValue()
        if isinstance(v, complex):
            low, high = 1+1j, 2+2j,
        else:
            low, high = 1, 2
        self.rnd.setInterval((low, high))
        self.assertEqual((low, high), self.rnd.getInterval())
        self.rnd.interval = (low, high)
        self.assertEqual((low, high), self.rnd.interval)

    def testGetSetSeed(self):
        seed = self.rnd.getSeed()
        seed += int(10 * abs(self.rnd.getValue()))
        self.rnd.setSeed(seed)
        self.assertEqual(seed, self.rnd.getSeed())
        rndseq1 = [self.rnd.getValue() for i in xrange(10)]
        self.rnd.setSeed(seed)
        self.assertEqual(seed, self.rnd.getSeed())
        rndseq2 = [self.rnd.getValue() for i in xrange(10)]
        self.assertEqual(rndseq1, rndseq2)
        # property
        seed = self.rnd.seed + long(10*abs(self.rnd()))
        self.rnd.seed = seed
        self.assertEqual(seed, self.rnd.seed)

# --------------------------------------------------------------------

class TestRandomRand(TestRandomBase, unittest.TestCase):
    RANDOM_TYPE = PETSc.Random.Type.RAND

class TestRandomRand48(TestRandomBase, unittest.TestCase):
    RANDOM_TYPE = PETSc.Random.Type.RAND48

## class TestRandomSPRNG(TestRandomBase, unittest.TestCase):
##     RANDOM_TYPE = PETSc.Random.Type.SPRNG

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
