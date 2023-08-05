if __name__ == '__main__':
    import sys, petsc
    petsc.Init(sys.argv)
    del sys, petsc
    

import petsc.PETSc as PETSc
import numpy.core as array


# ---------------------------------------------------
ops = PETSc.Options()

#ops['use_schur'] = 1
#ops['transpose'] = 1

USE_SCHUR = PETSc.Options.HasName('schur')
USE_MATIS = PETSc.Options.HasName('matis')
TRANSPOSE = PETSc.Options.HasName('transpose')
MONITOR   = PETSc.Options.HasName('monitor')

if USE_SCHUR or USE_MATIS:
    MAT_TYPE = PETSc.Mat.Type.IS
else:
    MAT_TYPE = PETSc.Mat.Type.MPIAIJ
    
if USE_SCHUR:
    #KSP_TYPE = PETSc.KSP.Type.RICHARDSON
    KSP_TYPE = PETSc.KSP.Type.PREONLY
    PC_TYPE  = PETSc.PC.Type.SCHUR
    ops['pc_schur_ksp_type']  = 'cg'
    if MONITOR:
        ops['pc_schur_ksp_monitor'] = 'stdout'
else:
    KSP_TYPE = PETSc.KSP.Type.CG
    #PC_TYPE  = PETSc.PC.Type.JACOBI
    PC_TYPE  = None
    if MONITOR:
        ops['ksp_monitor'] = 'stdout'

# ---------------------------------------------------

def Poisson3D(H, ndof, lgmap, gridshape):
 
    n0, n1, n2 = gridshape
    e0, e1, e2 = n0-1, n1-1, n2-1

    nodes = array.arange(n0*n1*n2, dtype=PETSc.Int).reshape(n0, n1, n2)

    icone = array.zeros((e0,e1,e2, 8))
    icone[:,:,:,0] = nodes[ 0:n0-1 , 0:n1-1, 0:n2-1 ]
    icone[:,:,:,1] = nodes[ 1:n0   , 0:n1-1, 0:n2-1 ]
    icone[:,:,:,2] = nodes[ 1:n0   , 1:n1  , 0:n2-1 ]
    icone[:,:,:,3] = nodes[ 0:n0-1 , 1:n1  , 0:n2-1 ]
    icone[:,:,:,4] = nodes[ 0:n0-1 , 0:n1-1, 1:n2   ]
    icone[:,:,:,5] = nodes[ 1:n0   , 0:n1-1, 1:n2   ]
    icone[:,:,:,6] = nodes[ 1:n0   , 1:n1  , 1:n2   ]
    icone[:,:,:,7] = nodes[ 0:n0-1 , 1:n1  , 1:n2   ]
    icone.shape = (e0*e1*e2, 8)
    icone = icone[:, [4,5,6,7,0,1,2,3]]

    elmat = [[ 4,  0, -1,  0,  0, -1, -1, -1],
             [ 0,  4,  0, -1, -1,  0, -1, -1],
             [-1,  0,  4,  0, -1, -1,  0, -1],
             [ 0, -1,  0,  4, -1, -1, -1,  0],
             [ 0, -1, -1, -1,  4,  0, -1,  0],
             [-1,  0, -1, -1,  0,  4,  0, -1],
             [-1, -1,  0, -1, -1,  0,  4,  0],
             [-1, -1, -1,  0,  0, -1,  0,  4]]
    elvec = [1] * 8

    elmat = 1.0/(12*H) * array.array(elmat, dtype=PETSc.Scalar)
    elvec = 1.0/8      * array.array(elvec, dtype=PETSc.Scalar)

    A = PETSc.Mat.Create(PETSc.COMM_WORLD)
    A.setSizes(ndof)
    A.setType(MAT_TYPE)
    A.setLGMapping(lgmap)
    A.setPreallocation(27)
    x, b = A.getVecs()
    x.setLGMapping(lgmap)
    b.setLGMapping(lgmap)
    
    ADD_VALUES = PETSc.InsertMode.ADD_VALUES
    A_setValues = A.setValuesLocal
    b_setValues = b.setValuesLocal
    for elem in icone:
        A_setValues(elem, elem, elmat, ADD_VALUES)
        b_setValues(elem,       elvec, ADD_VALUES)
    A.assemble()
    b.assemble()
    return A, b, x


COMM = PETSc.COMM_WORLD
size = COMM.getSize()
rank = COMM.getRank()


NDIM  = 3

#SHAPE = 3, 3, 3
#SHAPE = 5, 5, 5
SHAPE = 10, 10, 10
#SHAPE = 20, 20, 20
#SHAPE = 30, 30, 30
#SHAPE = 40, 40, 40

PART  = 2, 2, 2
BBOX = [(0.0, 1.0)] * 3

h =[(bb[1]-bb[0])/(SHAPE[i]-1)
    for i,bb in enumerate(BBOX)]
H = array.product(h)

from Grid import Grid
grid = Grid(SHAPE, bbox=BBOX, part=PART, pid=rank)

NDOF = array.product(SHAPE)
snodes = grid.nodes.copy()

lgmap = PETSc.LGMapping(snodes, comm=COMM)
A, b, x = Poisson3D(H, NDOF, lgmap, snodes.shape)

if rank==0:
    bnd = [0], [0]
else:
    bnd = [], []
A.zeroRowsLocal(bnd[0])
b.setValuesLocal(bnd[0], bnd[1])
b.assemble()

ksp = PETSc.KSP(ksp_type=KSP_TYPE, pc_type=PC_TYPE, comm=COMM)
ksp.setFromOptions()

same_nz = PETSc.Mat.Structure.SAME_NONZERO_PATTERN
ksp.setOperators(A, A, same_nz)

if USE_SCHUR:
    if not TRANSPOSE:
        solve = ksp.pc.apply
    else:
        solve = ksp.pc.applyTranspose
    solve = ksp.solve
else:
    if not TRANSPOSE:
        solve = ksp.solve
    else:
        solve = ksp.solveTranspose


from time import time

for i in xrange(0):
    x.set(0)
    t = time()
    solve(b,x)
    t = time()-t
    PETSc.Print('time: %f\n'% (t,))

same_nz = PETSc.Mat.Structure.SAME_NONZERO_PATTERN
ksp.setOperators(A,A,same_nz)

for i in xrange(0):
    x.set(0)
    t = time()
    solve(b,x)
    t = time()-t
    PETSc.Print('time: %f\n'% (t,))

solve(b,x)


r = x.duplicate()
if not TRANSPOSE:
    A.mult(x,r)
else:
    A.multTranspose(x,r)
r.axpy(-1,b)

fmt  = 'residual: norm: %f  min: %f  sum: %f max:%f\n'
args = (r.norm(), r.min()[1], r.sum(), r.max()[1])
PETSc.Print(fmt % args)

## A.getDiagonal(r)
## fmt  = 'diagonal: norm: %f  min: %f  sum: %f max:%f\n'
## args = (r.norm(), r.min()[1], r.sum(), r.max()[1])
## PETSc.Print(fmt % args)


## A.getRowMax(r)
## fmt  = 'rowmax:   norm: %f  min: %f  sum: %f max:%f\n'
## args = (r.norm(), r.min()[1], r.sum(), r.max()[1])
## PETSc.Print(fmt % args)
