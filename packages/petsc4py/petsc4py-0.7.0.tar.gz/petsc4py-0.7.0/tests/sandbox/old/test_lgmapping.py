import petsc.PETSc as PETSc
import numpy.core  as array

M, N = 5, 5 # grid sizes
P = 4       # processors

root = 0
rank = PETSc.WORLD_RANK
size = PETSc.WORLD_SIZE

def prn(obj=None, rank=rank, root=root):
    if rank==root:
        if obj:
            print obj
        else:
            print

if P != size:
    prn()
    prn('Please, run on 4 processors...')
    prn()
    raise SystemExit

# global grid
GIDX = array.arange(M*N).reshape(M,N)

# trivial partitioning
if rank % 2:
    j1,j2 = N/2,N
else:
    j1,j2 = 0,N/2+1

if rank < P/2:
    i1,i2 = 0,M/2+1
else:
    i1,i2 = M/2,M
   
# local grids
gidx = GIDX[i1:i2,j1:j2]
lidx = array.arange(gidx.size).reshape(gidx.shape)

# local to global mapping
lgmap = PETSc.LGMapping(gidx)
rank, ngh = lgmap.getInfo()
l2g = lgmap.apply(lidx.ravel())
g2l = lgmap.applyInverse(gidx)

# and now the output

prn()
prn("Using 'LGMapping' objects")
prn('=========================')
prn()


prn('Global Grid (Global Numbering)')
prn('------------------------------')
prn("%s" % GIDX)


prn('Local Grids (Global Numbering)')
prn('------------------------------')
PETSc.SequentialPhase().begin()
print "%d:\n%s\n" % (rank, gidx)
PETSc.SequentialPhase().end()


prn('Local Grids (Local Numbering)')
prn('------------------------------')
PETSc.SequentialPhase().begin()
print "%d:\n%s\n" % (rank, lidx)
PETSc.SequentialPhase().end()


prn("'LGMapping' object")
prn('------------------')
lgmap.view()
prn()


prn('Local Nodes -> Global Nodes')
prn('---------------------------')
PETSc.SequentialPhase().begin()
print "[%d] %s -> %s" % (rank, lidx.ravel(), l2g);
PETSc.SequentialPhase().end()
prn()


prn('Global Nodes -> Local Nodes')
prn('---------------------------')
PETSc.SequentialPhase().begin()
print "[%d] %s -> %s" % (rank, gidx.ravel(), g2l);
PETSc.SequentialPhase().end()
prn()

prn('Rank - Neighbors -> Local Shared Nodes (Local Numbering)')
prn('--------------------------------------------------------')
PETSc.SequentialPhase().begin()
print '\n'.join("[%d] - [%d] -> %s" \
                % (rank, p, ngh[p]) for p in ngh) + '\n'
PETSc.SequentialPhase().end()
