import sys

if '-N' in sys.argv:
    idx = sys.argv.index('-N')
    N = int(sys.argv[idx+1])
    del sys.argv[idx:(idx+1)]
else:
    N=3


from petsc import Initialize
Initialize(sys.argv)
#if '-help' in sys.argv:
#    sys.exit(0)

import petsc.PETSc as PETSc
import scipy.base  as array
from time import time

loops = 200

rank = PETSc.WORLD_RANK
size = PETSc.WORLD_SIZE


nodes = array.arange(N**3).reshape(N,N,N)
n0, n1, n2 = N, N, N
e0, e1, e2 = n0-1, n1-1, n2-1
nodes = array.arange(n0*n1*n2).reshape(n0, n1, n2)
icone = array.empty((e0, e1, e2, 8))
icone[:,:,:,0] = nodes[ 0:n0-1 , 0:n1-1, 0:n2-1 ]
icone[:,:,:,1] = nodes[ 1:n0   , 0:n1-1, 0:n2-1 ]
icone[:,:,:,2] = nodes[ 1:n0   , 1:n1  , 0:n2-1 ]
icone[:,:,:,3] = nodes[ 0:n0-1 , 1:n1  , 0:n2-1 ]
icone[:,:,:,4] = nodes[ 0:n0-1 , 0:n1-1, 1:n2   ]
icone[:,:,:,5] = nodes[ 1:n0   , 0:n1-1, 1:n2   ]
icone[:,:,:,6] = nodes[ 1:n0   , 1:n1  , 1:n2   ]
icone[:,:,:,7] = nodes[ 0:n0-1 , 1:n1  , 1:n2   ]
icone.shape = (e0*e1*e2, 8)

Ae = [[ 4,  0, -1,  0,  0, -1, -1, -1],
      [ 0,  4,  0, -1, -1,  0, -1, -1],
      [-1,  0,  4,  0, -1, -1,  0, -1],
      [ 0, -1,  0,  4, -1, -1, -1,  0],
      [ 0, -1, -1, -1,  4,  0, -1,  0],
      [-1,  0, -1, -1,  0,  4,  0, -1],
      [-1, -1,  0, -1, -1,  0,  4,  0],
      [-1, -1, -1,  0,  0, -1,  0,  4]]
Ae = array.asarray(Ae, dtype=PETSc.Scalar)




if rank != size-1:
    lnods = N**2 * (N-1)
else:
    lnods = N**3

(lnods, None)
A = PETSc.MatMPIAIJ((lnods, None), d_nz=27, o_nz=9)
x, b = A.getVecs()
A.setFromOptions()

start, end = A.getOwnershipRange()
gis = PETSc.ISStride(N**3, first=start)
lgmap = PETSc.LGMapping(gis)
A.setLGMapping(lgmap)
b.setLGMapping(lgmap)

addv = PETSc.InsertMode.ADD_VALUES
A_setvl = A.setValuesLocal
for idx in icone:
    A_setvl(idx, idx, Ae, addv)
A.assemble()
x.setRandom()
b.set(1)

if rank != size-1:
    bnd = array.array([])
else:
    bnd = nodes[-1,:,:]
A.zeroRowsLocal(bnd)
b.setValuesLocal(bnd, array.zeros(bnd.size, dtype=PETSc.Scalar))
b.assemble()

y = b.duplicate()

def test1(loops):
    A_mult = A.mult
    wt = time()
    for i in xrange(loops):
        A_mult(x, y)
    wt = time() - wt
    wt /= loops
    PETSc.SynchronizedPrint('[%d] %f\n'% (rank, wt))
    PETSc.SynchronizedFlush()


def test2(its):
    ksp = PETSc.KSP('cg', 'none')
    ksp.setOperators(A, A, PETSc.PC.Structure.SAME)
    ksp.setTolerances(rtol=0, atol=0, divtol=1e5, max_it=its)
    ksp.setFromOptions()
    ksp.solve(b, x)
    wt = time()
    ksp.solve(b, x)
    ksp.solve(b, x)
    wt = time() - wt
    wt /= its*2
    wt1 = PETSc.GlobalMin(wt)
    wt2 = PETSc.GlobalMax(wt)
    PETSc.Print('procs: %2d, ksp: CG, pc: NONE, sec/iter: [%f %f]\n'% (size, wt1, wt2))
    

if __name__ == '__main__':
    #test1(loops)
    test2(loops)
    
    
## vw = PETSc.ViewerDraw()
## vw(A)
## PETSc.Sleep(4)
