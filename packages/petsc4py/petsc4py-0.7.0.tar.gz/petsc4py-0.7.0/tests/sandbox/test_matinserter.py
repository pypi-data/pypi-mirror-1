from petsc import PETSc
from petsc.lib import _petsc as petsc

Inserter = petsc.MatGetInserter

mat = PETSc.MatSeqAIJ(6, bsize=2);

A1 = Inserter(mat, PETSc.InsertMode.INSERT, False, False)
A2 = Inserter(mat, PETSc.InsertMode.INSERT, False, True)


mat[range(6), range(6)] = PETSc.VecSeq(36).array
#mat.destroy()

A1[0,0] = 1
A1[4,4] = 1
mat.assemble()

print
mat.view()
print

#mat.destroy()

A2[0,0] = [1,2,3,4]
A2[1,1] = [5,6,7,8]
mat.assemble()

print
mat.view()
print

