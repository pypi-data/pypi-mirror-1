from __future__ import division
import sys
from petsc import Init; Init(sys.argv)
import petsc.PETSc as PETSc
import scipy.base  as array
from time import time


def Stiffness1D(N, L):
    N = int(N)
    L = float(L)
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

def Force1D(N, L, coefs):
    a, b, c = coefs
    x = array.linspace(0, L, N)
    return a * x**2 + b * x + c


N, L = 10, 1

A = Stiffness1D(N, L)

PETSc.Options.Set('ksp_type', 'cg')
#PETSc.Options.Set('ksp_type', 'gmres')
#PETSc.Options.Set('pc_type',  'jacobi')
PETSc.Options.Set('pc_type',  'none')
ksp = PETSc.KSP()
ksp.setOperators(A)
ksp.setFromOptions()


x1, b1 = A.getVecs()
b1.array = Force1D(N, L, [0, 0, 1])
b1.normalize()
ksp.solve(b1, x1)

x2, b2 = A.getVecs()
b2.array = Force1D(N, L, [0, 1, -1/2])
b2.normalize()
ksp.solve(b2, x2)

## x3, b3 = A.getVecs()
## b3.array = Force1D(N, L, [0, -1, 1/2])
## b3.normalize()
## ksp.solve(b3, x3)

rnd = PETSc.Random()
coefs = [rnd() for i in xrange(3)]
x, b = A.getVecs()
b.array = Force1D(N, L, coefs)

b.setRandom()
b.scale(0.1)
b.axpy(1,b1)
b.axpy(1,b2)


## xlist = [x1,x2,x3]
## blist = [b1,b2,b3]
xlist = [x1,x2,]
blist = [b1,b2]

for sol, rhs in zip(xlist, blist):
    alpha = b.dot(rhs)
    x.axpy(alpha, sol)

PETSc.Options.Set('ksp_monitor')
#PETSc.Options.Set('ksp_vecmonitor')
ksp.setFromOptions()
ksp.guess_nonzero = True

ksp.solve(b, x)

vw = PETSc.ViewerDraw()
