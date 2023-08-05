import petsc.PETSc as PETSc

rnd = PETSc.Random.Create(5,7)
PETSc.Print('interval: %s\n' % str(rnd.getInterval()))

values = [rnd() for i in xrange(3)]
PETSc.SynchronizedPrint('[%d] %s\n' % (PETSc.WORLD_RANK, values))
PETSc.SynchronizedFlush()
