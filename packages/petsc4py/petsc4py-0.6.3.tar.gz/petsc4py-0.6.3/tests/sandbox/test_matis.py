from petsc.PETSc import *

lgmap = LGMapping(range(4,10))

A = MatIS(10, lgmap)

for i in xrange(4,11):
    A[i,i] = 1

A.assemble()
A.view()
