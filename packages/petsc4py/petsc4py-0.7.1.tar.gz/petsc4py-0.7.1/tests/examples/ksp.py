# python ksp.py -pc_type none -ksp_monitor

import petsc4py, sys
petsc4py.init(sys.argv)
from petsc4py.PETSc import *

N = 100

A = Mat()
A.create()
A.setSizes(N)
A.setFromOptions()

x, b = A.getVecs()
b.setRandom()
A.diagonalSet(b)

ksp = KSP()
ksp.create()
ksp.setOperators(A,A,Mat.Structure.SAME_NONZERO_PATTERN)
ksp.setFromOptions()

#ksp.logResidualHistory()
ksp.solve(b,x)
#rh = ksp.getResidualHistory()
#ksp.view()
#print x.sum() / x.size
#print rh
