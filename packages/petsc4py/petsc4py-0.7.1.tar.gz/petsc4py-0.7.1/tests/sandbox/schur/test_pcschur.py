if __name__ == '__main__':
    import sys, petsc4py
    petsc4py.init(sys.argv)
    del sys, petsc4py
    

import petsc4py.PETSc as PETSc
import numpy as array


# ---------------------------------------------------
ops = PETSc.Options()

USE_SCHUR = 'use_schur' in ops
USE_MATIS = 'use_matis' in ops

if USE_MATIS:
    MAT_TYPE = PETSc.Mat.Type.IS
else:
    MAT_TYPE = PETSc.Mat.Type.AIJ

if USE_SCHUR:
    KSP_TYPE = PETSc.KSP.Type.PREONLY
    PC_TYPE  = PETSc.PC.Type.SCHUR
    #ops['ksp_max_it'] = 1
    ops['pc_schur_ksp_type']    = 'cg'
    ops['pc_schur_pc_type']     = 'jacobi'
    ops['pc_schur_ksp_monitor'] = None
else:
    KSP_TYPE = PETSc.KSP.Type.CG
    PC_TYPE  = PETSc.PC.Type.JACOBI
    ops['ksp_monitor'] = None

# ---------------------------------------------------

COMM = PETSc.COMM_WORLD
size = COMM.getSize()
rank = COMM.getRank()

# ---------------------------------------------------
M, N = 10,10

if  rank == 0:
    snodes = [0,3,4,1]
elif rank == 1:
    snodes = [1,4,5,2]
elif rank == 2:
    snodes = [3,6,7,4]
else:     
    snodes = [4,7,8,5]

gnodes = array.arange(M*N)

if 'rnd' in ops:
    import random
    random.seed(0)
    random.shuffle(gnodes)

gnodes.shape = (M,N)

if  rank == 0:
    iM, iN, = slice(0, M//2+1), slice(0,    N//2+1)
elif rank == 1:
    iM, iN, = slice(0, M//2+1), slice(N//2, N)
elif rank == 2:
    iM, iN, = slice(M//2, M),   slice(0,    N//2+1)
else:     
    iM, iN, = slice(M//2, M),   slice(N//2, N)

snodes = gnodes[iM,iN].flatten()
snodes = snodes[[0,2,3,1]]

lgmap = PETSc.LGMapping(snodes, comm=COMM)
A = PETSc.Mat().create(COMM)
A.setSizes(M*N)
A.setType(MAT_TYPE)
A.setLGMapping(lgmap)
x, b = A.getVecs()
x.setLGMapping(lgmap)
b.setLGMapping(lgmap)

ADD_VALUES = PETSc.InsertMode.ADD_VALUES
elmat = array.array([[  2,   -0.5, -1,   -0.5 ],
                     [ -0.5,  2,   -0.5, -1   ],
                     [ -1,   -0.5,  2,   -0.5 ],
                     [ -0.5, -1,   -0.5,  2   ]]) / 3
elrhs = array.array([1, 1, 1, 1],dtype=float)

if   rank==0:
    ifix = [0,1,3]; ifix = [0]
elif rank==1:
    ifix = [0,2,3]; ifix = [3]
elif rank==2:
    ifix = [0,1,2]; ifix = [1]
else:
    ifix = [1,2,3]; ifix = [2]

A.setValues(snodes,snodes,elmat,ADD_VALUES)
A.assemble()

A.zeroRowsLocal(ifix)
#A.zeroRowsLocal(array.arange(snodes.size))
b.setValues(snodes, elrhs, ADD_VALUES)
b.assemble()
b.setValuesLocal(ifix, [0]*len(ifix))
b.assemble()

x.set(0)


ksp = PETSc.KSP(ksp_type=KSP_TYPE, pc_type=PC_TYPE, comm=COMM)
ksp.setFromOptions()

same_nz = PETSc.Mat.Structure.SAME_NONZERO_PATTERN
ksp.setOperators(A, A, same_nz)

solve = ksp

solve(b,x)

r = x.duplicate()
A.mult(x,r)
r.axpy(-1,b)

fmt  = '[%d] min: %f  sum: %f max:%f\n'
args = (rank, r.min()[1], r.sum(), r.max()[1])
PETSc.Print(fmt % args)

ksp.view()
#pc = ksp.pc
#lgmap.view()
#pc.view()
