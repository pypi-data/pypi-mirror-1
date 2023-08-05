import petsc.PETSc as PETSc
import numpy.core  as array


class TSNLBE(PETSc.TS):

    class Problem(object):
        """
        Problem interface class
        """
        def __init__(self):
            self.__ts = None

        def setTS(self, ts):
            self.__ts = ts

        def getTS(self):
            return self.__ts

        def Function(self, snes, x, f):
            return NotImplementedError
        
        def Jacobian(self, snes, x, J, P):
            return NotImplementedError

    def __init__(self, comm=None):
        super(TSNLBE, self).__init__(comm=comm)
        self.setProblemType(PETSc.TS.ProblemType.NONLINEAR)
        self.setType(PETSc.TS.Type.BEULER)
        self.__setupcalled = False
        self.__snes_data = False
        self.__workvec = None
        
    def setUp(self):
        if self.__setupcalled:
            return
        problem, J, P = self.getProblemData()
        problem.setTS(self)
        super(TSNLBE, self).setUp()
        wvec = self.getSolution().duplicate()
        self.__workvec = wvec
        snes = self.getSNES()
        snes.setFunction(problem.Function, wvec)
        snes.setJacobian(problem.Jacobian, J, P)
        snes.ksp.reltol = 1 * snes.rtol
        self.__setupcalled = True
        
    def getProblemData(self):
        return self.__snes_data

    def setProblemData(self, problem, J, P=None):
        self.__snes_data = problem, J, P

    def step(self):
        self.setUp()
        return super(TSNLBE, self).step()



class HeatEq1D(TSNLBE.Problem):

    """
    1D Heat Equation
    """

    def __init__(self, N):
        self.N = N
        self.h = 1.0/(N+1)
        self.u_i   = PETSc.ScalarArray(N)
        self.u_im1 = PETSc.ScalarArray(N)
        self.u_ip1 = PETSc.ScalarArray(N)

    def Laplacian(self, U, U_xx, bc=(0, 0)):
        u_i, u_im1, u_ip1 = self.u_i, self.u_im1, self.u_ip1
        h = self.h
        # make stencil data
        U.getArray(u_i)
        u_im1[0]  = bc[0]; u_im1[1:]  = u_i[:-1]
        u_ip1[-1] = bc[1]; u_ip1[:-1] = u_i[1:]
        # laplacian 1d operator
        # u_{xx} = (u_{i-1} - 2*u_{i} + u_{i+1}) / h^2
        u_xx  = u_i
        u_xx *= -2
        u_xx += u_im1
        u_xx += u_ip1
        u_xx /= h**2
        # set y array
        U_xx.setArray(u_xx)

    def Function(self, snes, U_np1, F):
        # F(U_np1) = L(U) - 1/dt * (U_np1 - U_n)
        TS = self.getTS()
        U_n = TS.getSolution()
        dt = TS.getTimeStep()
        self.Laplacian(U_np1, F, [1, 0])
        F.AXPY(-1/dt, U_np1)
        F.AXPY( 1/dt, U_n)
        
    def Jacobian(self, snes, x, J, P):
        return PETSc.Mat.Structure.SAME_NONZERO_PATTERN
    
    def mult(self, x, y):
        # y = (L - 1/dt * I) * x
        dt = self.getTS().getTimeStep()
        self.Laplacian(x, y)
        y.AXPY(-1.0/dt, x)

    def multTranspose(self, x, y):
        self.Mult(x, y)

    def getDiagonal(self, D):
        D.set(2/self.h**2)
        

N  = 100

heat = HeatEq1D(N)
u = PETSc.Vec.CreateSeq(N)
u.set(0)
J = PETSc.Mat.CreateShell(N, context=heat)

ts = TSNLBE()
ts.setSolution(u)
ts.setProblemData(heat, J)

dt = 0.0025
tf = 0.25
nstep = int(tf/dt)
ts.setTimeStep(dt)
ts.setDuration(nstep, tf)

#PETSc.Options.Set('snes_mf')
PETSc.Options.Set('ksp_type', 'cg')
PETSc.Options.Set('pc_type', 'jacobi')
#PETSc.Options.Set('ksp_monitor')
PETSc.Options.Set('snes_monitor')
PETSc.Options.Set('ts_monitor')
PETSc.Options.Set('ts_vecmonitor')
ts.setFromOptions()

dt, tf =  ts.step()
ts.view()
