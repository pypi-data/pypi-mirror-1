import sys
import petsc.PETSc as PETSc

comm = PETSc.COMM_WORLD
rank = PETSc.WORLD_RANK
size = PETSc.WORLD_SIZE

message = 'I am process %2d of %2d\n' % (rank,size)
linesep = '='*len(message)+'\n'
header  = 'Hello World!'.center(len(message)) + '\n'

PETSc.Print(linesep)
PETSc.Print(header, PETSc.COMM_WORLD)
PETSc.Print(linesep)
PETSc.SynchronizedPrint(message, comm)
PETSc.SynchronizedFlush()
PETSc.Write(linesep, sys.stdout)
