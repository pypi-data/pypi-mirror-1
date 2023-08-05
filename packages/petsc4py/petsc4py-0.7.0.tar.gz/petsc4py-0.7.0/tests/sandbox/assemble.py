import mpi4py.MPI  as mpi
import petsc.PETSc as petsc
import numpy.core  as na


#from codetweaks import bind_all
#bind_all(petsc)
#bind_all(na)


n = 4
N = 1000

stride = na.arange(.1*N,.9*N,.8*N/n)

row = na.array(stride).astype(petsc.Int)
col = na.array(stride).astype(petsc.Int)
val = na.array(na.arange(n**2),
               dtype=petsc.Scalar).reshape(n,n)

A = petsc.MatSeqAIJ(N, 5)
A.option = petsc.Mat.Option.ROWS_SORTED
A.option = petsc.Mat.Option.COLUMNS_SORTED
A.option = petsc.Mat.Option.STRUCTURALLY_SYMMETRIC

nloops = 100 # inicial
pow    = 5

IM = petsc.InsertMode.INSERT_VALUES
#IM = petsc.InsertMode.ADD_VALUES
    
import petsc.lib._petsc as _petsc

for j in xrange(pow):

    A_setValues = A.setValues
    MatSetValues = _petsc.MatSetValues
    tic = mpi.Wtime()
    for i in xrange(nloops):
        MatSetValues(A, row, col, val, IM)
    toc1 = mpi.Wtime() - tic
    

    MatSetValues = _petsc.MatSetValues_Test
    tic = mpi.Wtime()
    for i in xrange(nloops):
        MatSetValues(A, row, col, val, IM)
    toc2 = mpi.Wtime() - tic

    tic = mpi.Wtime()
    for i in xrange(nloops):
        pass
    toc3  = mpi.Wtime() - tic
    
    print 'nloops:%10d, timing-> loop: %7.5f -  petsc: %7.5f - dummy: %7.5f' % \
          (nloops,toc3, toc1, toc2)
    
    nloops*=10

A.assemble()

#vw = petsc.ViewerDraw()
#vw(A)
