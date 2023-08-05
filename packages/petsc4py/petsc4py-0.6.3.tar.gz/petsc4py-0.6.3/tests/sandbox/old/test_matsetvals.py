import petsc.PETSc as PETSc

A = PETSc.MatSeqAIJ(5)

i = [0, 2, 4]
j = [1, 3]
v = [[1,2],
     [3,4],
     [5,6]]

A[i,j] = v
A.assemble()

print 'matrix (as dense):'
view = PETSc.ViewerASCII(format='dense', comm=A.comm)
view(A)

print

print 'non zeros:'
a = A[i,j]
print a
