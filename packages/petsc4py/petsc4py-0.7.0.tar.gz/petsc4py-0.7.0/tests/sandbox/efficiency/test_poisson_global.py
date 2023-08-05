import sys
from petsc import Initialize
Initialize(sys.argv)

import petsc.PETSc as PETSc
import scipy.base  as array

N = 32
H = 1.0/(N-1)

n0, n1, n2 = N, N, N
e0, e1, e2 = n0-1, n1-1, n2-1

nodes = array.arange(n0*n1*n2, dtype=PETSc.Int).reshape(n0, n1, n2)

icone = array.zeros((e0,e1,e2,8))
icone[:,:,:,0] = nodes[ 0:n0-1 , 0:n1-1, 0:n2-1 ]
icone[:,:,:,1] = nodes[ 1:n0   , 0:n1-1, 0:n2-1 ]
icone[:,:,:,2] = nodes[ 1:n0   , 1:n1  , 0:n2-1 ]
icone[:,:,:,3] = nodes[ 0:n0-1 , 1:n1  , 0:n2-1 ]
icone[:,:,:,4] = nodes[ 0:n0-1 , 0:n1-1, 1:n2   ]
icone[:,:,:,5] = nodes[ 1:n0   , 0:n1-1, 1:n2   ]
icone[:,:,:,6] = nodes[ 1:n0   , 1:n1  , 1:n2   ]
icone[:,:,:,7] = nodes[ 0:n0-1 , 1:n1  , 1:n2   ]
icone.shape = (e0*e1*e2,8)
icone = icone[:, [4,5,6,7,0,1,2,3]]

#print nodes
#print icone

elmat = [[ 4,  0, -1,  0,  0, -1, -1, -1],
         [ 0,  4,  0, -1, -1,  0, -1, -1],
         [-1,  0,  4,  0, -1, -1,  0, -1],
         [ 0, -1,  0,  4, -1, -1, -1,  0],
         [ 0, -1, -1, -1,  4,  0, -1,  0],
         [-1,  0, -1, -1,  0,  4,  0, -1],
         [-1, -1,  0, -1, -1,  0,  4,  0],
         [-1, -1, -1,  0,  0, -1,  0,  4]]
elvec = [1] * 8

elmat = 1.0/12 * array.array(elmat, dtype=PETSc.Scalar)
elvec = 1.0/8  * array.array(elvec, dtype=PETSc.Scalar)

nnod = nodes.size
A = PETSc.MatSeqAIJ(nnod, nz=27)
b = PETSc.VecSeq(nnod)
x = b.duplicate()

ADD_VALUES = PETSc.InsertMode.ADD_VALUES
A_setValues = A.setValues
b_setValues = b.setValues
for elem in icone:
    A_setValues(elem, elem, elmat, ADD_VALUES)
    b_setValues(elem,       elvec, ADD_VALUES)
    
A.assemble()
b.assemble()

A.scale(1/H)
b.scale(H)

bnd = [nodes[0, :, :], nodes[-1,  :,  :], 
       nodes[:, 0, :], nodes[ :, -1,  :], 
       nodes[:, :, 0], nodes[ :,  :, -1]]
bnd = list(b.flatten() for b in bnd)
bnd = array.concatenate(bnd)
bnd = array.unique(bnd)

#bnd = [0]

A.zeroRows(bnd)
b[bnd] = array.zeros(len(bnd), dtype=PETSc.Scalar)

ksp = PETSc.KSP(ksp_type='cg', pc_type='none')
ksp.setOperators(A)
ksp.setFromOptions()

#b.setRandom()
ksp.solve(b, x)

vwd = PETSc.ViewerDraw()
vwd(x)
print x.max()
