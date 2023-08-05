import sys
if '-petsc' in sys.argv:
    i = sys.argv.index('-petsc')
    argv  = [sys.argv[0]]
    argv += sys.argv[(i+1):]
    del sys.argv[i:]
    import petsc
    petsc.Initialize(argv)

# --------------------------------------------------------------------

from petsc4py import PETSc
import unittest
from sys import getrefcount

# --------------------------------------------------------------------

class Function:
    def __call__(self, snes, x, f):
        f[0] = x[0]*x[0] + x[0]*x[1] - 3.0;
        f[1] = x[0]*x[1] + x[1]*x[1] - 6.0;
        f.assemble()

class Jacobian:
    def __call__(self, snes, x, J, P):
        J[0,0] = 2.0*x[0] + x[1]; J[0,1] = x[0];
        J[1,0] = x[1];            J[1,1] = x[0] + 2.0*x[1];
        J.assemble()
        return PETSc.PC.Structure.SAME_NONZERO_PATTERN

# --------------------------------------------------------------------

class TestSNESBase(object):

    SNES_TYPE = None
    
    def setUp(self):
        snes = PETSc.SNES()
        snes.create(PETSc.COMM_SELF)
        if self.SNES_TYPE:
            snes.setType(self.SNES_TYPE)
        self.snes = snes

    def tearDown(self):
        if self.snes is None:
            return
        r,    fun = self.snes.getFunction()
        J, P, jac = self.snes.getJacobian()
        rc_fun = getrefcount(fun)
        rc_jac = getrefcount(jac)
        self.snes = None
        if fun is not None:
            self.assertEqual(getrefcount(fun), rc_fun-1)
        if jac is not None:
            self.assertEqual(getrefcount(jac), rc_jac-1)
        
    def testGetSetType(self):
        self.assertEqual(self.snes.getType(), self.SNES_TYPE)
        self.snes.setType(self.SNES_TYPE)
        self.assertEqual(self.snes.getType(), self.SNES_TYPE)
        
    def testTols(self):
        tols = self.snes.getTolerances()
        self.snes.setTolerances(*tols)
        tnames = ('atol','rtol', 'stol', 'max_it', 'max_funcs')
        tolvals = [getattr(self.snes, t) for t in  tnames]
        self.assertEqual(tols, tolvals)
        
    def testSetFunc(self):
        r = PETSc.Vec().createSeq(2)
        #self._fun_vec = r
        func = Function()
        refcnt = getrefcount(func)
        self.snes.setFunction(func, r)
        self.snes.setFunction(func, r)
        self.assertEqual(getrefcount(func), refcnt + 1)
        r2, func2 = self.snes.getFunction()
        self.assertEqual(r, r2)
        self.assertEqual(func, func2)
        self.assertEqual(getrefcount(func), refcnt + 2)
        r3, func3 = self.snes.getFunction()
        self.assertEqual(r, r3)
        self.assertEqual(func, func3)
        self.assertEqual(getrefcount(func), refcnt + 3)

    def testCompFunc(self):
        r = PETSc.Vec().createSeq(2)
        #self._fun_vec = r
        func = Function()
        self.snes.setFunction(func, r)
        x, y = r.duplicate(), r.duplicate()
        x[0:2] = [1, 2]
        self.snes.computeFunction(x, y)
        self.assertAlmostEqual(abs(y[0]), 0.0)
        self.assertAlmostEqual(abs(y[1]), 0.0)

    def testSetJac(self):
        J = PETSc.MatSeqAIJ(2)
        jac = Jacobian()
        refcnt = getrefcount(jac)
        self.snes.setJacobian(jac, J)
        self.snes.setJacobian(jac, J)
        self.assertEqual(getrefcount(jac), refcnt + 1)
        J2, P2, jac2 = self.snes.getJacobian()
        self.assertEqual(J, J2)
        self.assertEqual(J2, P2)
        self.assertEqual(jac, jac2)
        self.assertEqual(getrefcount(jac), refcnt + 2)
        J3, P3, jac3 = self.snes.getJacobian()
        self.assertEqual(J, J3)
        self.assertEqual(J3, P3)
        self.assertEqual(jac, jac3)
        self.assertEqual(getrefcount(jac), refcnt + 3)

    def testCompJac(self):
        J = PETSc.MatSeqAIJ(2)
        jac = Jacobian()
        self.snes.setJacobian(jac, J)
        x = PETSc.Vec().createSeq(2)
        x[0:2] = [1, 2]
        self.snes.computeJacobian(x, J)

    def testGetSetSol(self):
        x = PETSc.Vec().createSeq(2)
        #self._sol_vec = x
        x.setArray([2,3])
        self.snes.setSolution(x)
        xx =  self.snes.getSolution()
        self.assertEqual(x, xx)
        self.assertEqual(x.getRefCount(), 2)
        xx.destroy()
        self.assertFalse(xx)
        u = self.snes.getSolution()
        self.assertEqual(u.getRefCount(), 2)

    def testGetSetRhs(self):
        b = PETSc.Vec().createSeq(2)
        self.snes.setRhs(b)
        bb =  self.snes.getRhs()
        self.assertEqual(b, bb)
        self.assertEqual(b.getRefCount(), 3)
        
    def testGetKSP(self):
        ksp = self.snes.getKSP()
        self.assertEqual(ksp.getRefCount(), 2)

    def testSolve(self):
        J = PETSc.MatSeqAIJ(2)
        r = PETSc.Vec().createSeq(2)
        #self._jac_mat = J
        #self._fun_vec = r
        self.snes.setJacobian(Jacobian(), J)
        self.snes.setFunction(Function(), r)
        x = PETSc.Vec().createSeq(2)
        x.setArray([2,3])
        self.snes.setSolution(x)
        b = PETSc.Vec().createSeq(2)
        b.set(0)
        self.snes.setRhs(b)
        self.snes.setConvergenceHistory()
        self.snes.solve()
        rh, ih = self.snes.getConvergenceHistory()
        self.snes.setConvergenceHistory(0)
        rh, ih = self.snes.getConvergenceHistory()
        self.assertEqual(len(rh), 0)
        self.assertEqual(len(ih), 0)
        self.assertAlmostEqual(abs(x[0]), 1.0)
        self.assertAlmostEqual(abs(x[1]), 2.0)

    def testSetMonitor(self):
        reshist = {}
        def monitor(snes, its, fgnorm):
            reshist[its] = fgnorm
        refcnt = getrefcount(monitor)
        self.snes.setMonitor(monitor)
        self.assertEqual(getrefcount(monitor), refcnt + 1)
        self.testSolve()
        self.assertTrue(len(reshist) > 0)
        reshist = {}
        self.snes.clearMonitor()
        self.assertEqual(getrefcount(monitor), refcnt)
        self.testSolve()
        self.assertTrue(len(reshist) == 0)
        Monitor = PETSc.SNES.Monitor
        self.snes.setMonitor(Monitor())
        self.snes.setMonitor(Monitor.DEFAULT)
        self.snes.setMonitor(Monitor.SOLUTION)
        self.snes.setMonitor(Monitor.RESIDUAL)
        self.snes.setMonitor(Monitor.SOLUTION_UPDATE)
            
# --------------------------------------------------------------------

class TestSNESLS(TestSNESBase, unittest.TestCase):
    SNES_TYPE = PETSc.SNES.Type.LS

class TestSNESTR(TestSNESBase, unittest.TestCase):
    SNES_TYPE = PETSc.SNES.Type.TR

## class TestSNESTEST(TestSNESBase, unittest.TestCase):
##     SNES_TYPE = PETSc.SNES.Type.TEST
##     def setUp(self):
##         super(TestSNESTEST, self).setUp()
##         import tempfile
##         self.stdout = tempfile.TemporaryFile(mode='w+')
##         PETSc.SetStdout(self.stdout)
##     def tearDown(self):
##         super(TestSNESTEST, self).tearDown()
##         import sys
##         PETSc.SetStdout(sys.stdout)
##         self.stdout.flush()
##         self.stdout.close()
##         self.stdout = None
        
# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
