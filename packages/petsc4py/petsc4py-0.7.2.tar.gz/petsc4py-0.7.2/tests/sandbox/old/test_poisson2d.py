from __future__ import division

import petsc.PETSc as PETSc
import numpy.core  as array


N, M = 15, 15

H = 1.0/(N-1) * 1.0/(M-1)

# mesh

nodes = array.arange(N*M, dtype=PETSc.Int).reshape(N, M)

walls = (nodes[0,:], nodes[-1,:], # top, bottom
         nodes[:,0], nodes[:,-1]) # right, left

elems = array.zeros(((N-1),(M-1),4), PETSc.Int)
elems[..., 0] = nodes[ 0:N-1 , 0:M-1 ]
elems[..., 1] = nodes[ 1:N   , 0:M-1 ]
elems[..., 2] = nodes[ 1:N   , 1:M   ]
elems[..., 3] = nodes[ 0:N-1 , 1:M   ]
elems.shape = (elems.size//4, 4)

is_nod = PETSc.ISGeneral(nodes)
is_fix = array.concatenate(walls)
is_fix = PETSc.ISGeneral([]).expand(PETSc.ISGeneral(is_fix))
is_dof = is_nod.difference(is_fix)

nnod = is_nod.getSize()
ndof = is_dof.getSize()
nfix = is_fix.getSize()


A = PETSc.Mat.CreateSeqAIJ(ndof, nz=5);
x, b = A.getVecs()


idx = is_nod.getIndices()
dof = is_dof.getIndices()
fix = is_fix.getIndices()

idx[dof] = array.arange(len(dof))
idx[fix] = -1

ao_dof = PETSc.AOMapping(is_nod, PETSc.ISGeneral(idx))
ao_dof.ApplicationToPetsc(elems)


# element stiffness matrix
elmat = 1/(3*H) * array.array([[  2,   -0.5, -1,   -0.5 ],
                               [ -0.5,  2,   -0.5, -1   ],
                               [ -1,   -0.5,  2,   -0.5 ],
                               [ -0.5, -1,   -0.5,  2   ]],
                              PETSc.Scalar)

# element external forces vector
elvec = 1/4 * array.array([1, 1, 1, 1],
                          PETSc.Scalar)
# form linear system
ADD_VALUES = PETSc.InsertMode.ADD_VALUES
for e in elems:
    A.setValues(e, e, elmat, ADD_VALUES)
    b.setValues(e, elvec, ADD_VALUES)
A.assemble()
b.assemble()
x.set(0)


# linear system solution
ksp = PETSc.KSP()
ksp.setOperators(A)

PETSc.Options.Set('ksp_type', 'cg')
PETSc.Options.Set('pc_type', 'none')
PETSc.Options.Set('pc_type', 'ilu')
#PETSc.Options.Set('ksp_truemonitor')
PETSc.Options.Set('ksp_monitor')
PETSc.Options.Set('ksp_vecmonitor')
ksp.setFromOptions()

ksp.setNormType(ksp.NormType.UNPRECONDITIONED)
ksp.setConvergenceTest(PETSc.KSP.ConvergenceTest.SKIP)
ksp.max_it = 30

ksp.solve(b, x)

u = PETSc.Vec.CreateSeq(nnod)
sct = PETSc.Scatter(x, None, u, is_dof)
FW = PETSc.ScatterMode.FORWARD
IV = PETSc.InsertMode.INSERT_VALUES
sct(x, u, IV, FW)

vwd = PETSc.ViewerDraw()
vwd(u)
