"""
1D Heat Transfer problem

  u_{t} = u_{xx}, 0<t<T,  0<x<1
 u(0,x) = 0
 u(t,0) = 1
 u(t,1) = 0
"""

import petsc.PETSc as PETSc
import math

class HeatEq1D(PETSc.TS.RHSFunction):
    """
    1D Heat Equation
    """
    def __init__(self, N, bc=(0,0)):
        self.N = N
        self.bc = [float(i) for i in bc]
        self.h = 1.0/(N+1)
        self.u_i   = PETSc.ScalarArray(N)
        self.u_im1 = PETSc.ScalarArray(N)
        self.u_ip1 = PETSc.ScalarArray(N)

    def __call__(self, ts, t, U, U_t):
        h = self.h
        u_i, u_im1, u_ip1 = self.u_i, self.u_im1, self.u_ip1
        bc = self.bc
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
        U_t.setArray(u_xx)


N  = 100

ts = PETSc.TS(PETSc.TS.ProblemType.NONLINEAR,
              PETSc.TS.Type.BEULER)

heat = HeatEq1D(N, [1, 0])

ts.setRHSFunction(heat)

u = PETSc.Vec.CreateSeq(N)
u.set(0)
ts.setSolution(u)

dt = 0.0025
tf = 0.25
nstep = int(tf/dt)
ts.setTimeStep(dt)
ts.setDuration(nstep, tf)

PETSc.Options.Set('snes_mf')
PETSc.Options.Set('snes_monitor')
PETSc.Options.Set('ts_type', 'beuler')
PETSc.Options.Set('ts_vecmonitor')

def ts_monitor(ts, step, time, u):
    mesg = "TS timestep %d dt %g time %g\n" % \
           (step, ts.timestep, time)
    PETSc.Print(mesg, comm=ts.comm)


ts.clearMonitor()
ts.setMonitor(ts_monitor)

ts.setFromOptions()
dt, tf =  ts.step()
