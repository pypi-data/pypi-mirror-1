#/usr/bin/env python

import petsc.PETSc as petsc

rank = petsc.GetGlobalRank();
size = petsc.GetGlobalSize();

import numpy.core as na

P0,P1 = 2,2  # processors in each direction

N0,N1 = 5,7  # grid points in each direction

N = N0*N1 # total grid points
P = P0*P1 # total processors

if P!= size: raise RuntimeError,'must run in %d processors' % P

from mpi4py import mpi

p0,p1 = rank%P0,rank/P0 # procs id in each direction

n0b,n0e = mpi.distribute(N0,P0,p0) 
n1b,n1e = mpi.distribute(N1,P1,p1)


n0 = n0e-n0b;
n1 = n1e-n1b;
n  = n0*n1;

indices = na.arange(N0*N1).reshape(N0,N1)
#petsc.Print(str(indices)+'\n')

indices = indices[n0b:n0e,n1b:n1e]
#petsc.SyncPrint(str(indices)+'\n'); petsc.SyncFlush()


# -----------
# Renumbering
# -----------
iset = petsc.ISGeneral(indices.flat)
#iset.View()

ao = petsc.AOBasic(iset)
#ao.View()


iset2 = iset.Copy()
ao.ApplicationToPetsc(iset2)

#lgmap = petsc.LGMap(iset2)
#lgmap.View()

#raise SystemExit


ib,ie = n0b,n0e
jb,je = n1b,n1e

if p0 != 0:
    ib-=1
    n0+=1
if p1 != 0:
    jb-=1
    n1+=1

#print '[%d]'%mpi.rank,'(%d,%d)'%(p0,p1),'i->%d:%d'%(ib,ie),'j->%d:%d'%(jb,je),
#raise SystemExit


# -----------
# Mesh
# -----------

nodes = na.arange(N0*N1).reshape(N0,N1)
#petsc.Print(str(nodes)+'\n')

nodes = nodes[ib:ie,jb:je]
#petsc.SyncPrint(str(nodes)+'\n'); petsc.SyncFlush()

quads = na.zeros(((n0-1)*(n1-1), 4), dtype=petsc.Int)

quads[:,0] = (nodes[ 0:n0-1 , 0:n1-1 ]).flat
quads[:,1] = (nodes[ 1:n0   , 0:n1-1 ]).flat
quads[:,2] = (nodes[ 1:n0   , 1:n1   ]).flat
quads[:,3] = (nodes[ 0:n0-1 , 1:n1   ]).flat

#petsc.SyncPrint('[%d]\n%s\n'%(rank,quads)); petsc.SyncFlush()


ao.ApplicationToPetsc(quads.flat)
#petsc.SyncPrint('[%d]\n%s\n'%(rank,quads)); petsc.SyncFlush()



A = petsc.MatMPIAIJ((n,n),(N,N),d_nz=5,o_nz=0);

em = 1.0/3.0 * na.asarray([[  2,   -0.5, -1,   -0.5 ],
                           [ -0.5,  2,   -0.5, -1   ],
                           [ -1,   -0.5,  2,   -0.5 ],
                           [ -0.5, -1,   -0.5,  2   ]]) # element stiff matrix


for q in quads:
    A.SetValues(q,q,em,A.ADD)
A.Assemble()

bnd = na.arange(0,N0*N1,N1)
isbnd = petsc.ISGeneral(bnd)
ao.ApplicationToPetsc(isbnd)

A.ZeroRows(isbnd,1)

b = petsc.VecMPI(n,N);
b.Set(1)


x = b.Duplicate();

if 1:
    ksp = petsc.KSP(petsc.KSP.CG)
else:
    ksp = petsc.KSP(petsc.KSP.GMRES)


if 1:
    #ksp.pc = petsc.PC(petsc.PC.BJACOBI)
    pass
else:
    #ksp.pc = petsc.PC(petsc.PC.JACOBI)
    pass



ksp.SetOperators(A)

ksp.guess_nonzero = True

x.Set(0)

#ksp.SetComputeEigenvalues(True)

ksp.Solve(b,x)

ksp.View()


x2 = x.Duplicate()
x2.Set(0)
sc = petsc.Scatter(x,iset2,x2,iset)

sc(x,x2,petsc.Scatter.INS,petsc.Scatter.FORWARD)

vw = petsc.ViewerDraw(position=(1500,0))
vw.View(x2)
