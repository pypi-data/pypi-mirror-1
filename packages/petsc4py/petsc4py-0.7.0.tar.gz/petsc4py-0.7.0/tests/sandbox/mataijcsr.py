import petsc.PETSc as petsc

i = range(0,21,3)
j = [0, 2, 4, 1, 3, 5]*3
v = [(k+1)*10 for k in xrange(len(j))]

M = petsc.MatMPIAIJ([(6,petsc.DECIDE),(petsc.DECIDE,6)],
                    csr=(i,j,v))

vwa = petsc.ViewerASCII(name='stdout', comm=M.comm)
vwi = petsc.ViewerASCII(format=petsc.ViewerASCII.Format.INFO,
                        comm=M.comm)
vwg = petsc.ViewerDraw(title='MatAIJ',
                       position=(0,0),
                       size='QUARTER_SIZE',
                       comm=M.comm)
vwa.View(M)
vwi.View(M)
vwg.View(M)



M = petsc.MatSeqAIJ([6,6],nz=2)
M.SetValuesCSR(i, j, v)
M.Assemble()

vwa = petsc.ViewerASCII(name='stdout', comm=M.comm)
vwi = petsc.ViewerASCII(format=petsc.ViewerASCII.Format.INFO,
                        comm=M.comm)
vwg = petsc.ViewerDraw(title='MatAIJ',
                       position=(0,0),
                       size='QUARTER_SIZE',
                       comm=M.comm)
vwa.View(M)
vwi.View(M)
vwg.View(M)
