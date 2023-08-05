#/usr/bin/env python


# Run Command : mpirun -np 4 bwpython -i fem.py
# -----------

import petsc
from mpi4py import mpi
import numarray as na

petsc.Init()

rank = mpi.rank
size = mpi.size



# Read and scatter mesh
# ---------------------

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

indices = na.arange(N0*N1, shape=(N0,N1))
#petsc.Print(str(indices)+'\n')

indices = indices[n0b:n0e,n1b:n1e]
#petsc.SyncPrint(str(indices)+'\n'); petsc.SyncFlush()

ib,ie = n0b,n0e
jb,je = n1b,n1e

if p0 != 0:
    ib-=1
    n0+=1
if p1 != 0:
    jb-=1
    n1+=1


nodes = na.arange(N0*N1, shape=(N0,N1))

nodes = nodes[ib:ie,jb:je]

quads = na.zeros(shape=((n0-1)*(n1-1),4),type=na.Int32)

quads[:,0] = (nodes[ 0:n0-1 , 0:n1-1 ]).flat
quads[:,1] = (nodes[ 1:n0   , 0:n1-1 ]).flat
quads[:,2] = (nodes[ 1:n0   , 1:n1   ]).flat
quads[:,3] = (nodes[ 0:n0-1 , 1:n1   ]).flat




# Renumbering
# -----------

iset = petsc.ISGeneral(indices.flat)
iset2 = iset.Copy()

appord = petsc.AOBasic(iset)

appord(iset2)
appord(quads.flat)


# Formulation
# -----------
class MyElement:
    # element stiff matrix
    em = 1.0/3.0 * na.array([[  2,   -0.5, -1,   -0.5 ],
                             [ -0.5,  2,   -0.5, -1   ],
                             [ -1,   -0.5,  2,   -0.5 ],
                             [ -0.5, -1,   -0.5,  2   ]],
                            type=petsc.Scalar)
    # element rhs
    ev = na.array([1,1,1,1],type=petsc.Scalar)

    def __call__(self,xnod,icone,Ae,be,**karg):
        Ae[:] = self.em
        be[:] = self.ev


# Linear System
# ---------------

# allocation

A = petsc.MatMPIAIJ((n,n),(N,N),d_nz=5,o_nz=0);
b = petsc.VecMPI(n,N);

# assembly

element = MyElement()
Ae = na.array(shape=(4,4), type=petsc.Scalar)
be = na.array(shape=(4,),  type=petsc.Scalar)

for e in quads:
    element(None,e,Ae,be)
    A.SetValues(e,e, Ae, A.ADD)
    b.SetValues(e,   be, b.ADD)
    
A.Assemble()
b.Assemble()

# boundary conditions

bnd = na.arange(0,N0*N1,N1)
bnd = petsc.ISGeneral(bnd)

appord(bnd)

A.ZeroRows(bnd,1)

del bnd




# Solve System
# -------------

if 1: ksp = petsc.KSP.CG
else: ksp = petsc.KSP.GMRES
   
if 1: pc = petsc.PC.BJACOBI
else: pc = petsc.PC.JACOBI

ksp      = petsc.KSP(ksp)
ksp.pc   = petsc.PC(pc)

ksp.eig   = True
ksp.rhist = [0.]*ksp.maxits

ksp.SetOperators(A)
ksp.guess_knoll  = True
#ksp.guess_nonzero = True

x = b.Duplicate()
x.Set(0)

ksp(b,x)



# Solution
# --------

sol = x.Duplicate()
scatter = petsc.Scatter(x,iset2,sol,iset)
scatter(x,sol,scatter.INS,scatter.FORWARD)

vw = petsc.ViewerDraw(pos=(1500,0))
vw(sol)
