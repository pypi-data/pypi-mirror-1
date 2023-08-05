# -*- Python -*-

import petsc.PETSc as PETSc

def root():
    return PETSc.GetGlobalRank() == 0


import sys
class pstdout:
    def write(self,str):
        if root():
            sys.__stdout__.write(str)
sys.stdout = pstdout()


print """
Given the problem

      -del2(u) = f  in    (0,1)x(0,1)
         u = 0      on    Gamma

we solve it by the finite difference method
on a regular grid of N x N
using PETSc libraries under Python.
"""       

import PETSc
rank = PETSc.GetGlobalRank()
size = PETSc.GetGlobalSize()
hello_msg = 'Hello! I\'m process %d of %d.\n' % (rank,size)
print ''
#PETSc.SyncPrint(hello_msg)
#PETSc.SyncFlush()
print ''
print 'Done.'


print ''
print 'Problem Size:'
print '------------'
m = 10          # number of mesh points in x-direction
n = m           # number of mesh points in y-direction
hx = 1.0/(m-1)
hy = 1.0/(n-1)
ndof = m*n
print 'points_x =',m,' ','h_x =',hx
print 'points_y =',n,' ','h_x =',hy


print ''
print 'Stiffnes Matrix:'
print '---------------'
print 'five-point stencil 2D'

A = PETSc.MatMPIAIJ(PETSc.DECIDE,(ndof,ndof),d_nz=5,o_nz=1)

Istart,Iend = A.GetOwnershipRange();

## Set matrix elements for the 2-D, five-point stencil in parallel.
## - Each processor needs to insert only elements that it owns
##   locally (but any non-local elements will be sent to the
##   appropriate processor during matrix assembly). 
## - Always specify global rows and columns of matrix entries.

## Note: this uses the less common natural ordering that orders first
## all the unknowns for x = h then for x = 2h etc; Hence you see J = I +/- n
## instead of J = I +- m as you might expect. The more standard ordering
## would first do all variables for y = h, then y = 2h etc.
A.Assemble()
INSERT = PETSc.Mat.INSERT
for I in xrange(Istart,Iend) :
    v = -1.0; i = I/n; j = I - i*n;
    if i>0   : J = I - n; A.SetValue(I,J,v,INSERT)
    if i<m-1 : J = I + n; A.SetValue(I,J,v,INSERT)
    if j>0   : J = I - 1; A.SetValue(I,J,v,INSERT)
    if j<m-1 : J = I + 1; A.SetValue(I,J,v,INSERT)
    v = 4.0;          A.SetValue(I,I,v,INSERT)
A.Assemble()

#A.Scale(1/h)

vwA = PETSc.ViewerDraw('Stiffnes Matrix');
A.View(vwA)


print ' '
print 'Rigth Hand Side:'
print '---------------'
print 'f(x,y) := x*y'
f = lambda x,y : x*y;

b = PETSc.VecMPI(PETSc.DECIDE,ndof)
for j in xrange(n):
    for i in xrange(n):
        b.SetValue(i+j*n,f(i*hx,j*hy),b.INSERT)
del i,j
b.Assemble();

#b.Scale(h)

vwb = PETSc.ViewerDraw('Rigth Hand Side');
b.View(vwb)


print ' '
print 'Initial Guess:'
print '-------------'
x = b.Duplicate()
if 0:
    print 'x[i] = 0'
    x.Set(0)
else:
    print 'x[i] = random'
    x.SetRandom()

vwx0 = PETSc.ViewerDraw('Initial Guess');
x.View(vwx0)


print ' '
print 'Precontitioner Matrix:'
print '---------------------'
if 1:
    print 'Same Matrix'
    P = A
else:
    print 'Identity Matrix'
    P = PETSc.MatMPIAIJ((ndof,ndof),1)
    P.Shift(1) # Identity Matrix
    #P.Assemble()


## print ' '
## print 'SLES:'
## print '----'

## ksp  = PETSc.KSP(PETSc.GetCommWorld());
## pc   = PETSc.PC (ksp.GetPC());

## if 1:
##     print 'KSP: CG'
##     ksp.SetType(PETSc.KSP.CG)
## else:
##     print 'KSP: GMRES'
##     ksp.SetType(PETSc.KSP.GMRES)


## if 1:
##     print 'PC: ICC'
##     pc.SetType(PETSc.PC.BJACOBI)
## else:
##     print 'PC: NONE'
##     pc.SetType(PETSc.PC.NONE)

## ksp.SetOperators(A,P)
## ksp.SetRhs(b)
## ksp.SetSolution(x)

## ksp.SetInitialGuessNonzero(True)


## print ' '
## print 'Solving:'
## print '--------'
## ksp.Solve()
## print "iters: ",ksp.GetIterationNumber()
## print "rnorm: ",ksp.GetResidualNorm()


## print ''
## print 'SLES Info: (after solving)'
## print '---------'
## ksp.View()


# Generate MATLAB script
# ----------------------
def script():
    template = \
         """solution;
         m = %(M)s; n = %(N)s;
         
         x = linspace(0,1,n);
         y = linspace(0,1,m);
         
         [X,Y] = meshgrid(x,y);
         
         U = reshape(u,m,n);
         
         mesh(X,Y,U)
         """
    
    scr = template % {'M':m,'N':n}
    
    matlab = open('viewsol.m','w')
    matlab.write(scr)
    matlab.close()


#if root(): script()


# Use My CG Solver
# ------------

import solver
x.Set(0)
cg = solver.CG(A,b,x)
cg.maxit = ndof/2

#x.View()

cg.solve()


def anim():
    x.Set(0)
    cg.reset()
    for i in xrange(0,ndof/2):
        cg.step(1)
        x.View(vwx2)



vwx = PETSc.ViewerDraw('Solution');
x.View(vwx)

mtlb = PETSc.ViewerASCII('solution.m',);
mtlb.SetFormat(PETSc.ViewerASCII.MATLAB)
x.SetName('u')
x.View(mtlb)
del mtlb


if 0 :
    PETSc.Sleep(5)

if 0 :
    PETSc.Finalize()
