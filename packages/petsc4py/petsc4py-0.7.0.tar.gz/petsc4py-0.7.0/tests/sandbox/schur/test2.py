# -*- Python -*-

if __name__ == '__main__':
    import sys, petsc
    petsc.Init(sys.argv)
    del sys, petsc
    

import petsc.PETSc as PETSc
import numpy as array

COMM = PETSc.COMM_WORLD
SIZE = COMM.size
RANK = COMM.rank

USE_SCHUR = PETSc.Options.HasName('schur')
USE_MATIS = PETSc.Options.HasName('matis')
MONITOR   = PETSc.Options.HasName('monitor')

petscopts = PETSc.Options()

if USE_SCHUR:
    if SIZE > 1:
        USE_MATIS = True
    petscopts['ksp_type'] = 'preonly'
    petscopts['pc_type']  = 'schur'
    petscopts['pc_schur_ksp_type'] = 'cg'
    petscopts['pc_schur_pc_type']  = 'jacobi'
    if MONITOR:
        petscopts['pc_schur_ksp_monitor'] = 'stdout'
else:
    petscopts['ksp_type'] = 'cg'
    if MONITOR:
        petscopts['ksp_monitor'] = 'stdout'
    if USE_MATIS:
        petscopts['pc_type'] = 'jacobi'
    #else:
    #    petscopts['pc_type'] = 'jacobi'

M, N = (100,100)
hx = 1.0/(M-1)
hy = 1.0/(N-1)
ndof = M*N

A = PETSc.Mat()
A.create(comm=COMM)
A.setSizes(ndof)
if USE_MATIS:
    ldofs = array.arange(0,M*N)
    lgmap = PETSc.LGMapping(ldofs, comm=A.comm)
    A.setType(PETSc.Mat.Type.IS)
    A.setLGMapping(lgmap)
    A.setPreallocation(5)
else:
    A.setType(PETSc.Mat.Type.AIJ)
    A.setPreallocation([5, 1])

Istart,Iend = A.getOwnershipRange();

for I in xrange(Istart,Iend) :
    v = -1.0; i = I/N; j = I - i*N;
    if i>0   : J = I - N; A[I,J] = v
    if i<M-1 : J = I + N; A[I,J] = v
    if j>0   : J = I - 1; A[I,J] = v
    if j<M-1 : J = I + 1; A[I,J] = v
    v = 4.0;              A[I,I] = v
A.assemble()

#A.Scale(1/h)

x, b = A.getVecs()

x.set(0)

#f = lambda x,y : x*y;
f = lambda x,y : 1
for j in xrange(N):
    for i in xrange(M):
        b[i+j*N] = f(i*hx,j*hy)
del i,j
b.assemble();

#b.Scale(h)


#r,c = A.getOrdering('nd')
#A = A.permute(r,c)

ksp = PETSc.KSP(comm=COMM)
ksp.setOperators(A,A,PETSc.Mat.Structure.SAME)
ksp.setFromOptions()
ksp.solve(b,x)

#draw = PETSc.ViewerDraw(title='Matrix');
info = PETSc.ViewerASCII(name='stdout',format='info');

grid = array.arange(M*N).reshape(M,N)

def sep(string):
    indices = [int(i) for i in string.split()]
    grid = array.zeros((M,N))
    grid.flat[indices] = 1
    return grid
