import petsc.PETSc as PETSc

#PETSc.Options.Set('snes_monitor')
#PETSc.Options.Set('ksp_monitor')
#PETSc.Options.Set('snes_xmonitor')
#PETSc.Options.Set('ksp_xmonitor')

from sys import getrefcount

class MyFunction(PETSc.SNES.Function):
    def __call__(self, snes, x, f):
        f[0] = x[0]*x[0] + x[0]*x[1] - 3.0;
        f[1] = x[0]*x[1] + x[1]*x[1] - 6.0;
        f.assemble()

class MyJacobian(PETSc.SNES.Jacobian):
    def __call__(self, snes, x, J, P):
        J[0,0] = 2.0*x[0] + x[1]; J[0,1] = x[0];
        J[1,0] = x[1];            J[1,1] = x[0] + 2.0*x[1];
        J.assemble()
        return PETSc.PC.Structure.SAME_NONZERO_PATTERN
        
J = PETSc.MatSeqAIJ(2)
x = PETSc.Vec.CreateSeq(2)
r = x.duplicate()

snes = PETSc.SNES()
snes.type = 'ls'
#snes.type = 'tr'
#snes.type = 'test'
    
myfunction = MyFunction()
snes.setFunction(myfunction, r)

myjacobian = MyJacobian()
snes.setJacobian(myjacobian, J)
#PETSc.Options.Set('snes_fd')

tols = snes.getTolerances()
snes.setTolerances(*tols)

ksp = snes.ksp
ksp.type = PETSc.KSP.Type.GMRES

pc  = ksp.pc
pc.type  = PETSc.PC.Type.NONE

def ksp_monitor(ksp, its, rnorm):
    its = ksp.iternum
    rnorm = ksp.resnorm
    mesg = "  - %3d KSP  Residual norm: %14.12e\n" % (its, rnorm)
    PETSc.Print(mesg, comm=ksp.comm)

ksp.setMonitor(ksp_monitor)

def snes_monitor(snes, its, fgnorm):
    its = snes.iternum
    fgnorm = snes.funcnorm
    mesg = "+ %3d SNES   Function norm: %14.12e\n" % (its, fgnorm)
    PETSc.Print(mesg, comm=snes.comm)

snes.setMonitor(snes_monitor)

snes.setFromOptions()


x.array = [2,3]
snes.setSolution(x)
snes.solve()

info = [('SNES type'              , snes.type),
        ('abs tolerance'          , snes.atol),
        ('rel tolerance'          , snes.rtol),
        ('sol tolerance'          , snes.stol),
        ('max iterations'         , snes.max_it), 
        ('max function evals'     , snes.max_funcs),
        ('iteration number'       , snes.iternum),
        ('convergence reason'     , snes.converged),
        ('function norm'          , snes.funcnorm),
        ('num linear iterations'  , snes.linear_its),
        ('num unsuccessful steps' , snes.getNumberUnsuccessfulSteps()),
        ]

for i in info:
    print '%-22s -> %s' % i
