import numarray as array
import petsc.PETSc as PETSc


class Poisson1D(object):

    """
    1D Poisson problem

    -u_{xx} = 1 in x = (0,1)
          u = 0 on x = 0, 1
    """

    def __init__(self, N):
        self.N = N
        a = array.arange(1, N/2+1)
        a = array.concatenate([-a, a])
        self.D = PETSc.Vec.Create(N)
        self.D.setArray(a)
        self.D.reciprocal()
        self.D.view()
        
    def Mult(self, x, y):
        y.PointwiseMult(x, self.D)
        
    def MultTranspose(self, U, U_xx):
        self.Mult(U, U_xx)

    def GetDiagonal(self, D):
        self.D.Copy(D)

    def AssemblyBegin(self, type):
        pass
        
    def AssemblyEnd(self, type):
        pass



N = 10

matshell = Poisson1D(N)
A = PETSc.Mat.CreateShell(N, context=matshell)
A.Assemble()
PETSc.MatShell.SetContext(A, matshell)
ctx = PETSc.MatShell.GetContext(A)

x, b = A.GetVecs()
b.Set(0)
b.Set(1)

ksp_types = ["richardson",
             "chebychev",
             "cg",
             "cgne",
             "gmres",
             "fgmres",
             "lgmres",
             "tcqmr",
             "bcgs",
             "bcgsl",
             "cgs",
             "tfqmr",
             "cr",
             "lsqr",
             "preonly",
             #"qcg",
             "bicg",
             "minres",
             "symmlq"]

ksp_types = ['gmres']
#ksp_types = ['cg']
#ksp_types = []

def reason(r):
    reasons = PETSc.KSP.ConvergedReason.__dict__
    for k in reasons:
        if reasons[k] == r:
            return k

ksp = PETSc.KSP()
ksp.GetPC().SetType(PETSc.PC.Type.JACOBI)
ksp.SetOperators(A)

PETSc.Options.Set('ksp_monitor')
#PETSc.Options.Set('ksp_vecmonitor')
ksp.maxits = 1000
ksp.SetFromOptions()

for ksp_type in ksp_types:
    ksp.SetType(ksp_type)
    ksp.Solve(b, x)
    print '%-10s - %-14s - iters: %3d, ||r|| = %e' \
          % (ksp.type, reason(ksp.converged), ksp.iternum, ksp.resnorm)
    SLEEP = 2
    PETSc.Sleep(SLEEP)


vw = PETSc.ViewerDraw()
ksp.BuildSolution(x)
vw(x)
PETSc.Sleep(1)
r = x.Duplicate()
ksp.BuildResidual(r)
vw(r)

from sys import getrefcount as refcount
assert ctx is matshell
assert refcount(matshell) - 1 == 3
del ctx
assert refcount(matshell) - 1 == 2
del A
assert refcount(matshell) - 1 == 1
