if __name__ == '__main__':
    import sys, petsc
    petsc.Init(sys.argv)
    del sys, petsc
    

import petsc.PETSc as PETSc
import numpy.core as array


#A = PETSc.MatSeqAIJ(5)
A = PETSc.Mat()
A.create(PETSc.COMM_SELF)
A.setSizes(5)
A.setType('aij')
A.setUpPreallocation()
#A[0,0]=7
