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
        snes.ksp.rtol = snes.atol
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
        # diffusivity
        self.alpha = 1
        # number of grid points 
        self.N = N
        # grid spacing
        h = 1.0/(N+1)
        self.h = h
        # 1-D line elements
        self.mesh = PETSc.IntArray(shape=(N-1, 2))
        self.mesh [:, 0] = array.arange(N-1)
        self.mesh [:, 1] = self.mesh [:, 0] + 1
        # elemental stiffness matrix
        self.stiff = 1/h**2 * PETSc.ScalarArray((2,2), [[1, -1],
                                                        [-1, 1]])
        # elemental mass matrix
        self.mass  =   h/6  * PETSc.ScalarArray((2,2), [[2,  1],
                                                        [ 1, 2]])
        # auxiliar vector
        self.dU = PETSc.VecSeq(N)
        
    def Function(self, snes, U, F):
        # F(U) = 1/dt * M(U - U_n) + K(U)
        TS = self.getTS()
        dt = TS.getTimeStep()
        U_n = TS.getSolution()

        dU = self.dU
        U.copy(dU)
        dU.AXPY(-1,U_n)
        u = U.getArray()
        u_n = U_n.getArray()
        du = dU.getArray()
        
        mesh = self.mesh
        o_dt_mass = 1/dt * self.mass
        alpha_stiff = self.alpha * self.stiff
        fixa = ([0, self.N-1], [0, 0])

        ADD = PETSc.InsertMode.ADD_VALUES
        F.zeroEntries()
        for i, nodes in enumerate(mesh):
            res = array.dot(alpha_stiff, u[nodes])
            res -= array.dot(alpha_stiff, u_n[nodes])
            res += array.dot(o_dt_mass, du[nodes])
            F.setValues(nodes, res, ADD)
        F.assemble()
        F.setValues(*fixa)

    def Jacobian(self, snes, x, J, P):
        # J = 1/dt * M + K
        dt = self.getTS().getTimeStep()
        elmat = 1/dt * self.mass + self.alpha * self.stiff
        mesh = self.mesh
        
        ADD = PETSc.InsertMode.ADD_VALUES
        J.zeroEntries()
        for i, nodes in enumerate(mesh):
            J.setValues(nodes, nodes, elmat, ADD)
        J.assemble()
        J.zeroRows([0, N-1])
        
        return PETSc.Mat.Structure.SAME_NONZERO_PATTERN
    
N  = 5

heat = HeatEq1D(N)
u = PETSc.Vec.CreateSeq(N)
u[0] = 1


#J = PETSc.Mat.CreateShell(N, context=heat)
J = PETSc.Mat.CreateSeqAIJ(N)

ts = TSNLBE()
ts.setSolution(u)
ts.setProblemData(heat, J)

coeff = 100

heat.alpha *= coeff

dt = 0.001/coeff
tf = dt*10
nstep = int(tf/dt)
ts.setTimeStep(dt)
ts.setDuration(nstep, tf)


PETSc.Options.Set('snes_mf')
PETSc.Options.Set('ksp_type', 'cg')
PETSc.Options.Set('pc_type', 'jacobi')
#PETSc.Options.Set('pc_type', 'ilu')
PETSc.Options.Set('pc_type', 'none')
PETSc.Options.Set('ksp_monitor')
PETSc.Options.Set('snes_monitor')
PETSc.Options.Set('ts_monitor')
PETSc.Options.Set('ts_vecmonitor')
ts.setFromOptions()

def uminmonitor(ts, step, time, u):
    print u.min()
ts.setMonitor(uminmonitor)    

#ts.snes.setType('test')
ts.step()
#ts.view()

from math import sqrt
print 'delta:', heat.h/sqrt(4*heat.alpha*dt)
