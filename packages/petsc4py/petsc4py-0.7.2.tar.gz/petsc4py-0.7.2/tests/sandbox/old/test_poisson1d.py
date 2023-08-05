from __future__ import division
import sys
from petsc import Init; Init(sys.argv)
import petsc.PETSc as PETSc
import numarray    as array


class Poisson1D(object):

    def __init__(self, N=None, L=None):
        self.N = int(N or 10)
        self.L = float(L or 1)
        self.H = self.L/(self.N+1)
        self.u = PETSc.ScalarArray(self.N)
        self.aux = PETSc.ScalarArray(self.N)

    def getDiagonal(self, D):
        D.set(2/self.H**2)

    def mult(self, U, U_xx):
        H, u, aux = self.H, self.u, self.aux
        U.getArray(u)
        aux.flat = 0.0
        aux[0 ] =  0
        aux[-1] =  0
        aux[1:,] -= u[:-1]
        aux[:-1] -= u[1:]
        #aux /= H**2
        U_xx.setArray(aux)
        U_xx.scale(1/H**2)
        U_xx.AXPY(2/H**2, U)

    multTranspose = mult
        

def Stiffness1D(N=None, L=None):
    N = int(N or 10)
    L = float(L or 1)
    H = L/(N+1)

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
        

N, L = 10, 1

K1 = Stiffness1D(N, L)
K2 = PETSc.Mat.CreateShell(N, context=Poisson1D(N, L))

PETSc.Options.Set('ksp_type', 'cg')
PETSc.Options.Set('ksp_type', 'gmres')
PETSc.Options.Set('pc_type',  'jacobi')
#PETSc.Options.Set('pc_type',  'none')
PETSc.Options.Set('ksp_monitor')
PETSc.Options.Set('ksp_vecmonitor')
ksp = PETSc.KSP()
ksp.setFromOptions()

#from mpi4py import MPI

x1, b1 = K1.getVecs()
b1.set(1)

ksp.setOperators(K1)
#t1 = MPI.Wtime()
ksp.solve(b1, x1)
#t1 = MPI.Wtime() - t1
ksp.view()

r1 = x1.duplicate()
K1.mult(x1, r1)
r1.AYPX(-1, b1)

PETSc.Print('\n')



class Jacobi(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.comm = None
        
    def setUp(self):
        self.comm = self.matrix.comm
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
        
    
## jacobi = PETSc.PCShell(Jacobi(K2))
## ksp.setPC(jacobi)
## #ksp.setPCSide('left')
## ksp.setPCSide('right')


x2, b2 = K2.getVecs()
b2.set(1)

ksp.setOperators(K2)
#t2 = MPI.Wtime()
ksp.solve(b2, x2)
#t2 = MPI.Wtime() -t2
ksp.view()

#x2.view()

r2 = x2.duplicate()
K2.mult(x2, r2)
r2.AYPX(-1, b2)

#PETSc.Print('\n')
#PETSc.Print('t1: %f\n' % t1)
#PETSc.Print('t2: %f\n' % t2)


rnd = PETSc.Random()
a1, b1 = K1.getVecs()
a2, b2 = K2.getVecs()
a1.setRandom(rnd)
a1.copy(a2)

scale, shift = rnd(), rnd()

K1.scale(scale)
K1.shift(shift)
K2.scale(scale)
K2.shift(shift)

M = K1.norm()
eps = 2e-16
tol = eps * M

K1.mult(a1, b1)
K2.mult(a2, b2)
b1.AXPY(-1, b2)
assert b1.norm() < tol

K1.multTranspose(a1, b1)
K2.multTranspose(a2, b2)
b1.AXPY(-1, b2)
assert b1.norm() < tol

K1.getDiagonal(b1)
K2.getDiagonal(b2)
b1.AXPY(-1, b2)
assert b1.norm() < tol

print 'PC Side: %s' % ksp.pcside
