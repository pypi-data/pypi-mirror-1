import petsc.PETSc as PETSc

size = PETSc.COMM_WORLD.getSize()
rank = PETSc.COMM_WORLD.getRank()

seqphase = PETSc.SequentialPhase()

seqphase.begin()

print 'Hello World! I am PETSc in process %d of %d.' % (rank, size)

seqphase.end()

