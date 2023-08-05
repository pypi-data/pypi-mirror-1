#!bin/env python

import petsc.PETSc as petsc

# Change 'print' behavior to print only in proc 0
# by overriding sys.stdout

import sys
root = lambda: petsc.GetGlobalRank() == 0
class pstdout:
    def write(self,str):
        if root(): sys.__stdout__.write(str)
sys.stdout = pstdout()


print """
Given the problem

        -u''(x) = f(x)  in  (0,1)
      u(0)=u(1) = 0

If f(x)=1, the exat solution is

            u(x)= 1/2*x*(1-x)

we solve it by the finite element method
using PETSc libraries under Python.
"""



# Problem Size
intervals = 3000
n = intervals-1
h = 1.0/intervals

#Stiffnes Matrix
A = petsc.MatSeqAIJ((n,n),3)
A.SetValue(0,0,2,A.INS)
A.SetValue(0,1,-1,A.INS)
for i in xrange(1,n-1):
    A.SetValue(i,i,2,A.INS)
    A.SetValue(i,i-1,-1,A.INS)
    A.SetValue(i,i+1,-1,A.INS)
A.SetValue(n-1,n-2,-1,A.INS)
A.SetValue(n-1,n-1,2,A.INS)
A.Assemble()
A.Scale(1/h)

#A.View()
## vwb = petsc.ViewerBinary('qq.bin.dat')
## vwb(A)
## del vwb

## print ' '
## print 'Precontitioner:'
## print '---------------'
if 0:
    #print 'Same Matrix'
    P = A
else:
    #print 'Identity Matrix'
    P = petsc.MatSeqAIJ((n,n),1)
    P.ZeroEntries()
    P.Assemble()
    P.Shift(1)



# Rigth Hand Side:
f = lambda x: 1
#f = lambda x: -x*(x-1)
#f = lambda x: x

b = petsc.VecSeq(n)
for i in xrange(n):
    b.SetValue(i,f(i*h),b.INS)
del i

b.Scale(h)

#b.View()


## print '''
## Solution:
## --------'''
x = b.Duplicate()
x.Set(0)
#x.SetRandom()
#x.View()


## print '''
## Viewer:
## --------'''

vw = petsc.ViewerDraw()


## print '''
## KSP, PC:
## --------------'''

## ksp = petsc.KSP(petsc.GetCommWorld())
## pc  = petsc.PC(ksp.GetPC());

## if 1:
##     print 'KSP: CG'
##     ksp.SetType(petsc.KSP.CG)
## else:
##     print 'KSP: GMRES'
##     ksp.SetType(petsc.KSP.GMRES)


## if 1:
##     print 'PC: BJACOBI'
##     pc.SetType(petsc.PC.BJACOBI)
## else:
##     print 'PC: NONE'
##     pc.SetType(petsc.PC.NONE)


## ksp.SetOperators(A,P)
## ksp.SetRhs(b)
## ksp.SetSolution(x)

## ksp.SetInitialGuessNonzero(True)


## print '''
## Solving:
## --------'''
## x.Set(0)
## ksp.Solve()
## print "iters: ",ksp.GetIterationNumber()
## print "rnorm: ",ksp.GetResidualNorm()


## print '''
## KSP Info: (after solving)
## ---------'''
## ksp.View()


## print '''
## Numerical Solution:
## ------------------'''
## #x.View()


## print '''
## Exact Solution:
## ---------------'''
def u(x):
    y = 0.5*x*(1-x)
    return y
#for i in range(1,n+1): print u(i*h)


# My CG Solver
# ------------
import solver
cg = solver.CG(A,b,x)
cg.maxit = intervals/2
cg.maxit = intervals

#x.View()

#cg.solve()

def anim():
    #x.Set(0)
    cg.reset()
    #for i in range(0,intervals/2):
    i = 0
    while not cg.converged(): # and i<intervals:
        cg.step(1); i+=1
        x.View(vw)

# isr,isc = A.GetOrdering('nd')
# A.LUFactor(isr,isc)

## petsc.Finalize()
