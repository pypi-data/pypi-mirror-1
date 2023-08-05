import petsc.PETSc as PETSc


class Poisson1D(object):

    """
    1D Poisson problem

    -u_{xx} = 1 in x = (0,1)
          u = 0 on x = 0, 1
    """

    def __init__(self, N):
        self.N = N
        self.h = 1.0/(N+1)
        self.u_i   = PETSc.ScalarArray(N)
        self.u_im1 = PETSc.ScalarArray(N)
        self.u_ip1 = PETSc.ScalarArray(N)
        
    def setUpPreallocation(self):
        PETSc.Print('setUpPreallocation()\n')
        
        
    def mult(self, U, U_xx):
        h = self.h
        u_i, u_im1, u_ip1 = self.u_i, self.u_im1, self.u_ip1
        # make stencil data
        U.getArray(u_i)
        u_im1[-1] = 0 ; u_im1[:-1] = u_i[1:] 
        u_ip1[0]  = 0 ; u_ip1[1:]  = u_i[:-1]
        # calculate laplacian 1d operator
        # -u_{xx} = (-u_{i-1} + 2*u_{i} - u_{i+1}) / h^2
        u_xx  = u_i
        u_xx *= 2
        u_xx -= u_im1
        u_xx -= u_ip1
        u_xx /= h**2
        # set y array
        U_xx.setArray(u_xx)

    def multTranspose(self, U, U_xx):
        self.mult(U, U_xx)

    def getDiagonal(self, D):
        D.set(2/self.h**2)

    def assemblyBegin(self, type):
        pass
        
    def assemblyEnd(self, type):
        pass


N = 100

matshell = Poisson1D(N)
A = PETSc.Mat.CreateShell(N, context=matshell)
PETSc.MatShell.SetContext(A, matshell)

## A.setUpPreallocation()
## A.setUpPreallocation()
## A.setUp()
## A.setUp()
## A.setUp()
## A.setUp()

#a = PETSc.VecSeq(N)
#b = PETSc.VecSeq(N)
#A.mult(b,a)

#A.setUp()


ctx = A.getContext()

x, b = A.getVecs()
b.set(0)
b.set(1)

#A.mult(b, x)

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

ksp_types = ['cg']
#ksp_types = []

def reason(r):
    reasons = PETSc.KSP.ConvergedReason.__dict__
    for k in reasons:
        if reasons[k] == r:
            return k

ksp = PETSc.KSP()
ksp.getPC().setType(PETSc.PC.Type.JACOBI)
ksp.setOperators(A)

#PETSc.Options.Set('ksp_vecmonitor')
ksp.maxits = 1000
ksp.setFromOptions()


for ksp_type in ksp_types:
    ksp.setType(ksp_type)
    ksp.solve(b, x)
    print '%-10s - %-14s - iters: %3d, ||r|| = %e' \
          % (ksp.type, reason(ksp.converged), ksp.iternum, ksp.resnorm)
    SLEEP = 2
    PETSc.Sleep(SLEEP)


vw = PETSc.ViewerDraw()
ksp.buildSolution(x)
vw(x)
PETSc.Sleep(1)
r = x.duplicate()
ksp.buildResidual(r)
vw(r)

from sys import getrefcount as refcount

assert ctx is matshell
assert refcount(matshell) - 1 == 3
del ctx
assert refcount(matshell) - 1 == 2
A.setContext(None)
assert refcount(matshell) - 1 == 1
del A
assert refcount(matshell) - 1 == 1
