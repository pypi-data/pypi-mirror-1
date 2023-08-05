#!bin/env python

import petsc.PETSc as petsc


print """
Given the problem

        -u''(x) = f(x)  on  (0,1)
           u(x) = 0     at  x=0, x=1

If f(x)=1, the exat solution is

            u(x)= 1/2*x*(1-x)

We solve it by the finite difference method
using PETSc libraries under Python.
"""



# Problem Size
# ------------
n = 3000       # grid points, boundaries not included
h = 1.0/(n+1)  # grid spacing

# Stiffnes Matrix
# ---------------
A = petsc.MatSeqAIJ((n,n),3)
A.SetValue(0, 0,  2, A.INSERT)
A.SetValue(0, 1, -1, A.INSERT)
for i in xrange(1,n-1):
    A.SetValue(i, i,    2, A.INSERT)
    A.SetValue(i, i-1, -1, A.INSERT)
    A.SetValue(i, i+1, -1, A.INSERT)
A.SetValue(n-1, n-2, -1, A.INSERT)
A.SetValue(n-1, n-1,  2, A.INSERT)
A.Assemble()
A.Scale(1/h)

# Rigth Hand Side
# ---------------
def f(x):
    return 1

b = petsc.VecSeq(n)
for i in xrange(n):
    b.SetValue(i, f(i*h), b.INSERT)
b.Scale(h)


# KSP and PC
# ----------
ksp = petsc.KSP(type=petsc.KSP.BICG)
pc  = petsc.PC(type=petsc.PC.ILU)
ksp.SetPC(pc)


# Solve
# -----
x = b.Duplicate()
x.Set(0)
ksp.SetOperators(A)
ksp.Solve(b, x)


# Error respect to exact solution
# -------------------------------
def u(x):
    return 1.0/2*x*(1-x)

e = x.Duplicate()
for i in xrange(n):
    e.SetValue(i, u(i*h), b.INSERT)

e.AXPY(-1, x)

print "Error: %f" % e.Norm()


# View solution
# -------------
viewer = petsc.ViewerDraw()
viewer(x)

petsc.Sleep(3)
