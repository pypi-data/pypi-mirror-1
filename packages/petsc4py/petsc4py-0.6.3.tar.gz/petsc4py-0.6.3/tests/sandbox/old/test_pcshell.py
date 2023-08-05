from __future__ import division
import petsc.PETSc as PETSc


class Jacobi(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.comm = self.matrix.comm
        
    def setUp(self, *args):
        print args
        PETSc.Print('setUp()\n', comm=self.comm)

    def preSolve(self, *args):
        PETSc.Print('preSolve()\n', comm=self.comm)

    def postSolve(self, *args):
        PETSc.Print('postSolve()\n', comm=self.comm)
        
    def apply(self, x, y):
        PETSc.Print('apply()\n', comm=self.comm)
        self.matrix.getDiagonal(y)
        y.pointwiseDivide(x, y)

    def applyTranspose(self, x, y):
        PETSc.Print('applyTranspose()\n', comm=self.comm)
        self.apply(x, y)
    
    
def StiffMat1D(N=None, H=None):
    N = int(N or 10)
    H = float(H or 1/(N+1))
    K = PETSc.Mat.CreateSeqAIJ(N, nz=3)
    cols = PETSc.IntArray(3, [-1, 0, 1])
    vals = 1/H**2 * PETSc.ScalarArray(3, [-1, 2, -1])
    imode = PETSc.InsertMode.INSERT
    K[0, cols[1:]] = vals[1:]
    for row in xrange(1, N-1):
        cols += 1
        K.setValues(row, cols, vals, imode)
    K[N-1, cols[1:]] = vals[:-1]
    K.assemble()
    return K

N = 20

K = StiffMat1D(N)

PETSc.Options.Set('ksp_type', 'bicg')
PETSc.Options.Set('ksp_monitor')
PETSc.Options.Set('ksp_vecmonitor')

ksp = PETSc.KSP()
pc = ksp.getPC()
ksp.setFromOptions()

x1, b1 = K.getVecs()
b1.set(1)

ksp.setOperators(K)
pc.setType(PETSc.PC.Type.JACOBI)
ksp.solve(b1, x1)
ksp.view()

r1 = x1.duplicate()
K.mult(x1, r1)
r1.AYPX(-1, b1)

PETSc.Print('\n')

x2, b2 = K.getVecs()
b2.set(1)

pc = ksp.getPC()
pc.setType(PETSc.PC.Type.SHELL)
pcshell = Jacobi(K)
## PETSc.PCShell.SetContext(pc, pcshell)
## ctx = PETSc.PCShell.GetContext(pc)
## PETSc.PCShell.SetName(pc, type(ctx).__name__)

pc = PETSc.PCShell(pcshell)
ctx = PETSc.PCShell.GetContext(pc)
ksp.setPC(pc)
ksp.setOperators(K)
ksp.solve(b2, x2)
ksp.view()

r2 = x2.duplicate()
K.mult(x2, r2)
r2.AYPX(-1, b2)

from sys import getrefcount as refcount
assert ctx is pcshell
assert refcount(pcshell) - 1 == 3
del ctx
assert refcount(pcshell) - 1 == 2
del pc, ksp
assert refcount(pcshell) - 1 == 1
