# -*- Python -*-

if __name__ == '__main__':
    import sys, petsc4py
    petsc4py.init(sys.argv)
    del sys, petsc4py
    

import petsc4py.PETSc as PETSc
import numpy as array

COMM = PETSc.COMM_WORLD
SIZE = COMM.size
RANK = COMM.rank

opts = PETSc.Options()

USE_SCHUR = ('schur')   in opts
USE_MATIS = ('matis')   in opts
MONITOR   = ('monitor') in opts
VIEW      = ('view')    in opts

M, N = (31,31)
M, N = (4,4)
ggrid = array.arange(M*N).reshape(M,N)

if RANK%2 == 0:
    jb, je = 0, N//2+1
else:
    jb, je = N//2, N 

if RANK//2 == 0:
    ib, ie = 0, M//2+1 
else:
    ib, ie = M//2, M 

#PETSc.SyncPrint('[%d] i:(%d,%d) j:(%d,%d)\n' % (RANK,ib,ie,jb,je))
#PETSc.SyncFlush()

lgrid = ggrid[ib:ie,jb:je]
m, n = lgrid.shape

quads = array.zeros(((m-1)*(n-1),4))

quads[...,0] = lgrid[ 0:m-1 , 0:n-1 ].flat
quads[...,1] = lgrid[ 1:m   , 0:n-1 ].flat
quads[...,2] = lgrid[ 1:m   , 1:n   ].flat
quads[...,3] = lgrid[ 0:m-1 , 1:n   ].flat
quads.shape = (quads.size/4,4)

A = PETSc.Mat()
A.create(comm=COMM)
A.setSizes(M*N)
if USE_MATIS:
    A.setType(PETSc.Mat.Type.IS)
else:
    A.setType(PETSc.Mat.Type.AIJ)
lgmap = PETSc.LGMapping(lgrid.flat, comm=COMM)
A.setLGMapping(lgmap)
A.setPreallocation([5, 1])

b, x = A.getVecs()

# element matrix
em = 1.0/3.0 * array.array([[  2,   -0.5, -1,   -0.5 ],
                            [ -0.5,  2,   -0.5, -1   ],
                            [ -1,   -0.5,  2,   -0.5 ],
                            [ -0.5, -1,   -0.5,  2   ]],
                           dtype=PETSc.Scalar)
# element rhs
ev = array.array([1,1,1,1],dtype=PETSc.Scalar)

fix = [[0,N-1,(M-1)*N,M*N-1][RANK]]
#fix = [[0],[],[],[]][RANK]
#fix = [[M/4*N],[],[],[]][RANK]

kappa=1
#kappa=(RANK+1)
ADD = PETSc.InsertMode.ADD_VALUES
for q in quads:
    A.setValues(q,q,kappa*em,ADD)
A.assemble()
A.zeroRows(fix)

for q in quads:
    b.setValues(q,ev,ADD)
b.assemble()
b.set(1)
b.setValues(fix,[0]*len(fix))
b.assemble()

PETSc.SyncPrint('[%d] %s\n' % (RANK, A.range))
PETSc.SyncFlush()
PETSc.Print('%s\n\n' % ggrid)

x.set(0)

if USE_SCHUR:
    opts['ksp_type'] = 'preonly'
    opts['pc_type']  = 'schur'
    opts['pc_schur_ksp_type'] = 'cg'
    if MONITOR:
        opts['pc_schur_ksp_monitor'] = 'stdout'
else:
    opts['ksp_type'] = 'cg'
    if USE_MATIS:
        opts['pc_type']  = 'jacobi'
    else:
        opts['pc_type']  = 'jacobi'
    if MONITOR:
        opts['ksp_monitor'] = None
if VIEW:
    opts['ksp_view'] = None


ksp = PETSc.KSP(comm=COMM)
ksp.setOperators(A,A,PETSc.Mat.Structure.SAME)
ksp.setFromOptions()
ksp.solve(b,x)

#draw = PETSc.ViewerDraw(title='Matrix');
#info = PETSc.ViewerASCII(name='stdout',format='info');

#draw(x)

#if not RANK: print array.arange(m*n).reshape(m,n)
PCSetUp OnBlocks KSPSetUp
