import time
import petsc.PETSc as PETSc
import numpy.core  as array
import math



class HeatEq3D(object):

    def __init__(self, N=None, L=None):
        # grid points
        if N is None:
            self.N = [10] * 3
        else:
            assert len(N) == 3
            self.N = list(int(n) for n in N)
        # domain length
        if L is None:
            self.L = [1.0] * 3
        else:
            assert len(L) == 3
            self.L = list(float(l) for l in L)
        # grid sizes
        self.H = [l/(n+1) for l, n in zip(self.L, self.N)]
        # auxiliar arrays
        self.u_i = PETSc.ScalarArray(self.N)
        self.u_s = PETSc.ScalarArray(self.N)
        self.aux = PETSc.ScalarArray(self.N)

    def getDiagonal(self, D):
        d = sum(-2.0/h**2 for h in self.H)
        D.set(d)

    def mult(self, U, U_t):
        H, u_i, u_s, aux = self.H, self.u_i, self.u_s, self.aux

        # get solution array
        u_s.flat = 0.0
        U.getArray(u_i)
        
        # first dimension
        aux.flat = 0
        aux[0,   :, :] =  0
        aux[-1,  :, :] =  0
        aux[1:,  :, :] += u_i[:-1, :, :]
        aux[:-1, :, :] += u_i[1:,  :, :]
        aux /= H[0]**2
        array.add(u_s, aux, u_s)
        # second dimension
        aux.flat = 0
        aux[:,   0, :] =  0
        aux[:,  -1, :] =  0
        aux[:, 1:,  :] += u_i[:, :-1, :]
        aux[:, :-1, :] += u_i[:, 1:,  :]
        aux /= H[1]**2
        array.add(u_s, aux, u_s)
        # third dimension
        aux.flat = 0
        aux[:, :,   0] =  0
        aux[:, :,  -1] =  0
        aux[:, :,  1:] += u_i[:, :, :-1]
        aux[:, :, :-1] += u_i[:, :, 1: ]
        aux /= H[2]**2
        array.add(u_s, aux, u_s)

        U_t.setArray(u_s)
        alpha = sum(-2.0/h**2 for h in H)
        U_t.AXPY(alpha, U)

    multTranspose = mult


opts = PETSc.Options()
opts['ksp_type']      = 'cg'
opts['pc_type']       = 'none'
#opts['ksp_monitor']   = True
#opts['ts_monitor']    = True
#opts['ts_vecmonitor'] = True

def run(nnods):
    N = (nnods,) * 3
    u_0 = 10
    heateq3d = HeatEq3D(N)
    ndof = array.product(heateq3d.N)
    A = PETSc.MatShell(ndof, context=heateq3d)
    u = PETSc.Vec.CreateSeq(ndof)
    u.set(u_0)

    ts = PETSc.TS(PETSc.TS.ProblemType.LINEAR)
    ts.setRHSMatrix(None, A)
    ts.setType(PETSc.TS.Type.BEULER)
    ts.setSolution(u)

    dt = 0.005
    tf = 0.1 + dt
    nts = int(tf/dt)
    ts.setTimeStep(dt)
    ts.setDuration(nts, tf)
    ts.setFromOptions()

    t = time.time()
    dt, tf = ts.step()
    t = time.time() - t

    return t

timing = []
run(2)
start = 5
end   = 10
step  = 1

evals = 1
for n in xrange(start, end, step):
    t = 0
    for i in xrange(evals):
        t += run(n)
    t /= evals
    timing.append(t)
    print '%3d %f' %(n, t)
    
