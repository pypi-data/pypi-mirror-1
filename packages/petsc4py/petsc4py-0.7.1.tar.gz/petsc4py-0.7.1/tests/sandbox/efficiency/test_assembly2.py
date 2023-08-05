import sys, time
from petsc import Initialize
Initialize(sys.argv)

import petsc.PETSc as PETSc
import scipy.base  as array


def assemble(A, indices, Ae):
    loops = 1
    imode = PETSc.InsertMode.ADD_VALUES
    A_setValues = A.setValues
    _time = time.time
    t = _time()

    for idx in indices:
        A_setValues(idx, idx, Ae, imode)
    A.assemble()
    
    t = _time() - t
    t /= loops
    return t

#N = 4
N = 32
#N = 64
N += 1
H = 1.0/(N-1)

n0, n1, n2 = N, N, N
e0, e1, e2 = n0-1, n1-1, n2-1

nodes = array.arange(n0*n1*n2).reshape(n0, n1, n2)
icone = array.empty((e0,e1,e2,8))
icone[:,:,:,0] = nodes[ 0:n0-1 , 0:n1-1, 0:n2-1 ]
icone[:,:,:,1] = nodes[ 1:n0   , 0:n1-1, 0:n2-1 ]
icone[:,:,:,2] = nodes[ 1:n0   , 1:n1  , 0:n2-1 ]
icone[:,:,:,3] = nodes[ 0:n0-1 , 1:n1  , 0:n2-1 ]
icone[:,:,:,4] = nodes[ 0:n0-1 , 0:n1-1, 1:n2   ]
icone[:,:,:,5] = nodes[ 1:n0   , 0:n1-1, 1:n2   ]
icone[:,:,:,6] = nodes[ 1:n0   , 1:n1  , 1:n2   ]
icone[:,:,:,7] = nodes[ 0:n0-1 , 1:n1  , 1:n2   ]
icone.shape = (e0*e1*e2,8)

nen, ndof  = icone.shape[1], 4
sz = nen*ndof
Ae = array.zeros((sz, sz), dtype=PETSc.Scalar)
for i in xrange(ndof):
    Ae[i*nen:(i+1)*nen, i*nen:(i+1)*nen] = 1

indices = array.empty((icone.shape[0], icone.shape[1]*ndof), dtype=PETSc.Int)
for i, ico in enumerate(icone):
    aux = ico*ndof + array.arange(ndof).reshape(ndof,1)
    indices[i, :] = aux.transpose().ravel()


def renumber(elems, L):
    #if elems.size == 1:
    #    L.append(int(elems))
    #    return
    if elems.size <= 1**3:
        L.extend(int(i) for i in elems.ravel())
        return
    
    idx = [(slice(0, sz//2), slice(sz//2, sz))
           for sz in elems.shape]
    part = []
    for i in xrange(2):
        ii = idx[0][i]
        for j in xrange(2):
            ij = idx[1][j]
            for k in xrange(2):
                ik = idx[2][k]
                e = elems[ii,ij,ik]
                part.append(e)
    for els in part:
        renumber(els, L)

Ne = N-1
elems = array.arange(Ne**3).reshape(Ne, Ne, Ne)
L = []
renumber(elems, L)
perm = array.array(L, dtype=PETSc.Int)
assert array.all(array.sort(perm)==array.arange(len(indices)))



nnod = nodes.size
msize = nnod * ndof

A = PETSc.MatSeqAIJ(msize, nz=27*ndof)
A.option = PETSc.Mat.Option.DO_NOT_USE_INODES
#A.options = PETSc.Mat.Option.IGNORE_ZERO_ENTRIES


idx0 = indices.copy()
t0 = assemble(A, idx0, Ae)


## idx1 = indices.copy()
## t1 = assemble(A, idx1, Ae)


## t2 = 0
## for i in xrange(ndof):
##     idx2 = -array.ones(indices.shape, indices.dtype)
##     j = array.arange(i*nen, (i+1)*nen)
##     idx2[:, j] = indices[:, j]
##     t2 += assemble(A, idx2, Ae)


## idx3 = -array.ones(indices.shape, indices.dtype)
## t3 = assemble(A, idx3, Ae)


idx4 = indices[perm, :]
t4 = assemble(A, idx4, Ae)


import random
random.shuffle(perm)
#assert array.all(array.sort(perm)==array.arange(len(indices)))
idx5 = indices[perm, :]
t5 = assemble(A, idx5, Ae)



#tt = (t0, t1, t2, t3, t4, t5)
tt = (t0, t4, t5)
print ('%f '* len(tt)) % tt
