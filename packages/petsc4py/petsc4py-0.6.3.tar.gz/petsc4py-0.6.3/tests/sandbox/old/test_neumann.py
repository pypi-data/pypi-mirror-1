"""
Neumann problem in 1D with iterative and direct solvers.
"""

import sys
from petsc import Init
Init(sys.argv)

import petsc.PETSc as PETSc
import numpy.core  as array

# Problem Size
N = 11        # grid points
h = 1.0/(N-1) # element size

# Stiffnes Matrix
A = PETSc.MatSeqAIJ(N,nz=3)
im = PETSc.IntArray(2, [0, 1])
jm = im
em = 1/h * PETSc.ScalarArray((2,2), [[1, -1],[-1, 1]])
for i in xrange(0,N-1):
    A.setValues(im+i,jm+i,em,PETSc.InsertMode.ADD)
A.assemble()

# Force Vector
b = PETSc.VecSeq(N)
b.array = xrange(0,N)
b.scale(h)

# Residual
r = b.duplicate()

# Constant Null Space
nsp = PETSc.NullSpace(has_const=1)
A.attachNullSpace(nsp)
nsp.remove(b)

# Krylov Solver
ksp = PETSc.KSP(PETSc.KSP.Type.CG)
pc  = PETSc.PC(PETSc.PC.Type.NONE)
ksp.setPC(pc)
ksp.setComputeEigenvalues(True)
ksp.setOperators(A)
x1 = b.duplicate()
ksp.solve(b, x1)
A.mult(x1, r)
r.AYPX(-1, b)
print 'krylov: |r|: %g' % r.norm()


# LU Solver
luopts = {'shiftnz':   1e-66,
          'zeropivot': 0.0,
        }
LU = A.copy()
order = PETSc.Mat.OrderingType.ND
order = PETSc.Mat.OrderingType.NATURAL
rp, cp= A.getOrdering(order)
luopts = LU.LUFactor(rp, cp, luopts)
x2 = b.duplicate()
LU.solve(b, x2)
nsp(x2)
A.mult(x2, r)
r.AYPX(-1, b)
print 'direct: |r|: %g' % r.norm()


## # ILUFactor
## iluopts = {#'shiftpd': True,
##           #'shiftpd': False,
##           'shiftnz': 1e-14,
##           'zeropivot': 1e-14,
##           #'zeropivot': 0,
##           }
## ILU = A.Copy()
## rp, cp= A.GetOrdering(PETSc.Mat.OrderingType.ND)
## rp = cp = PETSc.ISStride(N)
## rp.ToGeneral()
## rp.SetPermutation()
## rp.SetIdentity()
## iluopts = ILU.ILUFactor(rp, cp, iluopts)
## x3 = b.Duplicate()
## ILU.Solve(b, x3)
## nsp(x3)
## A.Mult(x3, r)
## r.AYPX(-1, b)
## print 'direct: |r|: %g' % r.Norm()


# Viewers
vwi = PETSc.ViewerASCII(format=PETSc.ViewerASCII.Format.INFO)
vwa = PETSc.ViewerASCII()
vwd = PETSc.ViewerDraw()
