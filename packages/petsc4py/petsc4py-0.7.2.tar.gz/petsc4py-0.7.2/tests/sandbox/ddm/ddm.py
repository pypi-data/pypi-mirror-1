if __name__ == '__main__':
    import sys, petsc
    petsc.Init(sys.argv)
    del sys, petsc
    

import petsc.PETSc as PETSc

class Domain(object):

    def __init__(self, lgmap=None, idx_B=None):
        # members
        # + local to global mapping
        self.lgmap = None 
        # index sets
        self.is_S = None # local subdomain nodes, local numbering
        self.is_I = None # local interior nodes, local numbering
        self.is_B = None # local interface nodes, local numbering
        # + sizes 
        self.sizes = None
        # + vector scatters
        self.S2I = None # local subdomain to local interior
        self.S2B = None # local subdomain to local interface
        self.B2G = None # local interface to global interface
        # + flags for scatters
        self.INSERT  = PETSc.InsertMode.INSERT_VALUES
        self.ADD     = PETSc.InsertMode.ADD_VALUES
        self.FORWARD = PETSc.ScatterMode.FORWARD
        self.REVERSE = PETSc.ScatterMode.REVERSE
        # build object
        if lgmap is not None:
            self.build(lgmap, idx_B)

    def __del__(self):
        self.__init__()

    def build(self, lgmap, idx_B=None):
        # check local to global mapping
        isinstance(lgmap, PETSc.LGMapping)
        self.lgmap = lgmap
        
        # global communicator
        COMM = self.getComm()
        # sequential communicator
        COMM_SELF = PETSc.COMM_SELF
        
        # create a parallel index set with all subdomain nodes in
        # local natural numbering (using stride index set)
        sdsize = self.lgmap.getSize()
        self.is_S = PETSc.ISStride(size=sdsize, comm=COMM_SELF)

        # calculate inter-processors ghosts nodes between this
        # processor and others in local natural numbering using
        # information provided by 'LGMapping' object.
        # In the uniprocessor case neighbor information is just an
        # empty mapping as there are not shared interface nodes.
        neighs = self.lgmap.getInfo()
        ghosts = neighs.get(self.lgmap.comm.rank, [])
        ghosts = PETSc.ISGeneral(ghosts, comm=COMM_SELF)

        # determine interface nodes in local natural numbering
        if idx_B is None:
            # interface nodes are the ghost ones
            is_B = ghosts
        else:
            # interface nodes are the union of ghost nodes and
            # provided interface nodes
            if isinstance(idx_B, PETSc.IS):
                idx_B = idx_B.getIndices()
            is_B = PETSc.ISGeneral(idx_B, comm=COMM_SELF)
            del interface
            is_B = ghosts.expand(is_B)
            ghosts.destroy()
        self.is_B = is_B
        self.is_B.sort()
        
        # calculate interior nodes in this subdomain in local natural
        # numbering using index set difference
        # {interior} = {subdomain} - {interface}
        self.is_I = self.is_S.difference(is_B) # already sorted

        # determine index set of local interface nodes
        # in global natural [0, size(interface)) numbering
        idxB = self.is_B.getIndices()
        self.lgmap.apply(idxB, idxB)
        is_G =  PETSc.ISGeneral(idxB, comm=COMM)
        del idxB
        # remove duplicates expanding an empty index set
        empty = PETSc.ISGeneral([], comm=PETSc.COMM_SELF)
        all_B = is_G.allGather()
        all_B = empty.expand(all_B)
        empty.destroy()
        # calculate interface nodes in global domain
        # in a global natural interface numbering
        size_G = all_B.getLocalSize()
        all_Bn = PETSc.ISStride(size=size_G, comm=COMM_SELF)
        aomap = PETSc.AOMapping(all_B, all_Bn)
        aomap.ApplicationToPetsc(is_G)
        all_B.destroy()
        all_Bn.destroy()
        aomap.destroy()
        
        size_S = self.is_S.getLocalSize()
        size_I = self.is_I.getLocalSize()
        size_B = self.is_B.getLocalSize()

        # build vector scatters
        vec_S = PETSc.VecSeq(size_S)
        vec_I = PETSc.VecSeq(size_I)
        vec_B = PETSc.VecSeq(size_B)
        vec_G = PETSc.VecMPI(size_G, comm=COMM)
        # - from local subdomain nodes to local interior nodes
        self.S2I  = PETSc.Scatter(vec_S, self.is_I, vec_I, None)
        # - from local subdomain nodes to local interface nodes
        self.S2B  = PETSc.Scatter(vec_S, self.is_B, vec_B, None)
        # - from local interface to global interface
        self.B2G = PETSc.Scatter(vec_B, None, vec_G, is_G)
        is_G.destroy()
        #self.is_G = is_G
        
        # sizes
        self.sizes = ((size_I, size_B), vec_G.getSizes())
      
        vec_S.destroy()
        vec_I.destroy()
        vec_B.destroy()
        vec_G.destroy()

    def getComm(self):
        """
        """
        return self.lgmap.getComm()

    def getLGMapping(self):
        """
        """
        return self.lgmap
    
    def getIndices(self):
        """
        """
        return (self.is_I, self.is_B)

    def getSizes(self):
        """
        """
        return self.sizes

    def split(self, vec_S, vec_I, vec_B, imode=None):
        """
        vec_S[i_I, i_B] --> [vec_I, vec_B]
        """
        imode = imode or self.INSERT
        smode = self.FORWARD
        if vec_I is not None:
            self.S2I.scatter(vec_S, vec_I, imode, smode)
        if vec_B is not None:
            self.S2B.scatter(vec_S, vec_B, imode, smode)
        
    def join(self, vec_I, vec_B, vec_S, imode=None):
        """
        [vec_I, vec_B] --> vec_S[i_I, i_B] 
        """
        imode = imode or self.INSERT
        smode = self.REVERSE
        if vec_I is not None:
            self.S2I.scatter(vec_I, vec_S, imode, smode)
        if vec_B is not None:
            self.S2B.scatter(vec_B, vec_S, imode, smode)

    def gather(self, vec_G, vec_B, imode=None):
        """
        vec_G[B] --> vec_B
        """
        imode = imode or self.INSERT
        smode = self.REVERSE
        self.B2G.scatter(vec_G, vec_B, imode, smode)

    def scatter(self, vec_B, vec_G, imode=None):
        """
        vec_B + vec_G[B] --> vec_G[B]
        """
        imode = imode or self.ADD
        smode = self.FORWARD
        self.B2G.scatter(vec_B, vec_G, imode, smode)



class MatSC(object):

    def __init__(self, domain=None, solver=None):
        # members
        # + Domain object
        self.domain = None
        # + local matrix
        self.A = None 
        self._state = None # state of local matrix
        # + submatrices
        self.A_II = None # submatrix interior  - interior 
        self.A_IB = None # submatrix interior  - interface
        self.A_BI = None # submatrix interface - interior 
        self.A_BB = None # submatrix interface - interface
        self._submats = None  # all submatrices
        # + local interior solver
        self.inv_A_II = None
        # + global interface scaling vector
        self.D = None
        # + work vectors
        self.u_I, self.v_I = None, None # local interior 
        self.u_B, self.v_B = None, None # local interface
        # build object
        if domain is not None:
            self.build(domain, solver)
        
    def __del__(self):
        self.__init__()
        
    def build(self, domain, solver=None):
        # check Domain object
        assert isinstance(domain, Domain)
        self.domain = domain
        # create/check local solver
        if solver is None:
            solver = PETSc.KSP(comm=PETSc.COMM_SELF)
            solver.setType(PETSc.KSP.Type.PREONLY)
            solver.getPC().setType(PETSc.PC.Type.LU)
        else:
            assert isinstance(solver, PETSc.KSP)
        self.inv_A_II = solver
        # create work vectors
        nI, nB = self.domain.getSizes()[0]
        self.u_I, self.v_I = PETSc.VecSeq(nI), PETSc.VecSeq(nI)
        self.u_B, self.v_B = PETSc.VecSeq(nB), PETSc.VecSeq(nB)
        # scaling vector will be created on demand
        self.D = None

    def getComm(self):
        return self.domain.getComm()

    def getSizes(self):
        lsize, gsize = self.domain.getSizes()[1]
        return ((lsize, lsize), (gsize, gsize))
        
    def getDomain(self):
        return self.domain
    
    def getSolver(self):
        return self.inv_A_II
        
    def getScaling(self):
        if self.D is None:
            vsize = self.domain.getSizes()[1]
            vcomm = self.getComm()
            self.D = PETSc.VecMPI(vsize, comm=vcomm)
            self.u_B.set(1.0)
            self.domain.scatter(self.u_B, self.D)
        return self.D

    def getMatrix(self):
        if self.A is None:
            raise ValueError('matrix not set')
        return self.A

    def setMatrix(self, A, reuse=False):
        # check local matrix
        assert isinstance(A, PETSc.Mat)
        # determine action to do
        if self.A != A:
            self.A = A
            build_submats = True
        elif not reuse or self._submats is None:
            build_submats = True
        elif self._state != A.getState():
            build_submats = False
        else:
            return # nothing to do !!
        # build/update local submatrices
        iI, iB = self.domain.getIndices()
        if build_submats:
            A_II = A.getSubMatrix(iI, iI)
            A_IB = A.getSubMatrix(iI, iB)
            A_BI = A.getSubMatrix(iB, iI)
            A_BB = A.getSubMatrix(iB, iB)
            self.A_II, self.A_IB = A_II, A_IB
            self.A_BI, self.A_BB = A_BI, A_BB
        else:
            A_II, A_IB = self.A_II, self.A_IB
            A_BI, A_BB = self.A_BI, self.A_BB
            A.getSubMatrix(iI, iI, A_II)
            A.getSubMatrix(iI, iB, A_IB)
            A.getSubMatrix(iB, iI, A_BI)
            A.getSubMatrix(iB, iB, A_BB)
        # update submatrices, state and local solver
        self._submats = (A_II, A_IB, A_BI, A_BB)
        self._state  = A.getState()
        same_nz = PETSc.PC.Structure.SAME_NONZERO_PATTERN
        self.inv_A_II.setOperators(A_II, A_II, same_nz)

    def getSubMatrices(self):
        return self._submats
    
    def getDiagonal(self, d):
        self.A_BB.getDiagonal(self.u_B)
        d.zeroEntries()
        self.domain.scatter(self.u_B, d)

    def mult(self, x, y):
        """
        Global matrix-vector product of global Schur complement matrix
        and an interface vector. The main steps are:

          - Gather values at indices 'B' from global interface vector
            'x' to a sequential vector 'x_B'::

               x_B  <- x[B]

          - Apply Schur complement operator locally to 'x_B' vector
            and generate result into a sequential vector 'y_B'::

               y_B  <- (A_BB - A_BI * inv(A_II) * A_IB) * x_B
            
          - Assemble values from local sequential interface vector
            'y_B' to global interface vector 'y' at indices 'B'::

               y[B] <- y[B] + y_B
        """
        u_I, u_B = self.u_I, self.u_B
        v_I, v_B = self.v_I, self.v_B

        y.zeroEntries()
        
        self.domain.gather(x, u_B)
        self.A_IB.mult(u_B, u_I)         # u_I <= A_IB * u_B
        self.inv_A_II.solve(u_I, v_I)    # v_I <= inv(A_II) * u_I  
        self.A_BI.mult(v_I, v_B)         # v_B <= A_BI * v_I
        v_B.scale(-1)                    # v_B <= -v_B
        self.A_BB.multAdd(u_B, v_B, v_B) # v_B <= A_BB * u_B + v_B
        self.domain.scatter(v_B, y)

    def buildGuess(self, x, xG):
        """
        Builds a initial guess by averaging interface values from each
        subdomain.
        """
        x_I, x_B = self.u_I, self.u_B
        
        xG.zeroEntries()
        self.domain.split(x, None, x_B)
        self.domain.scatter(x_B, xG)
        D = self.getScaling()
        xG.pointwiseDivide(xG, D)

    def buildRhs(self, b, bG):
        """
        Builds global interface right hand side `bG` from local
        subdomain right hand side `b`::

           b_I   <- b[I]
           b_B   <- b[B]
           bG[B] <- bG[B] +  b_B - A_BI * inv(A_II) * b_I
        """
        u_I, u_B = self.u_I, self.u_B
        b_I, b_B = self.v_I, self.v_B

        bG.zeroEntries()
        self.domain.split(b, b_I, b_B)
        self.inv_A_II.solve(b_I, u_I)
        self.A_BI.mult(u_I, u_B)
        b_B.axpy(-1, u_B)
        self.domain.scatter(b_B, bG)
        
    def buildSolution(self, xG, b, x):
        """
        Builds local subdomain solution `x` from global interface
        solution `xG` and local subdomain right hand side `b`::

           x_B    <- xG[B]
           x_I    <- inv(A_II) * (b_I - A_IB * x_B)
           x[I,B] <- [x_I, x_B]
        """
        b_I, b_B = self.u_I, self.u_B
        x_I, x_B = self.v_I, self.v_B
        
        self.domain.gather(xG, x_B)
        self.domain.split(b, b_I, None)
        self.A_IB.mult(x_B, x_I)
        b_I.axpy(-1.0, x_I)
        self.inv_A_II.solve(b_I, x_I)
        self.domain.join(x_I, x_B, x)



class Solver(object):

    def __init__(self, lgmap=None, ksp_L=None, ksp_G=None):
        # members
        self.domain = None # Domain object
        self.mat_A  = None # local matrix
        self.str_A  = None # local matrix structure
        self.mat_S  = None # schur complement matrix
        self.ksp_L  = None # local solver
        self.ksp_G  = None # gloabal solver
        self.vec_b  = None # rhs work vector
        self.vec_x  = None # sol work vector
        # setup flag
        self._setup = False 
        # build object
        if lgmap is not None:
            self.build(lgmap, ksp_L, ksp_G)
            
    def __del__(self):
        self.__init__()
        
    def build(self, lgmap, ksp_L=None, ksp_G=None):
        # local to gloabal mapping
        assert isinstance(lgmap, PETSc.LGMapping)
        # Domain object
        if self.domain is None:
            self.domain = Domain(lgmap)
        else:
            self.domain.build(lgmap)
        # local solver
        if ksp_L is not None:
            assert isinstance(ksp_L, PETSc.KSP)
            self.ksp_L = ksp_L
        elif self.ksp_L is None:
            self.ksp_L = PETSc.KSP(comm=PETSc.COMM_SELF)
            self.ksp_L.setType(PETSc.KSP.Type.PREONLY)
            self.ksp_L.getPC().setType(PETSc.PC.Type.LU)
        # global solver
        if ksp_G is not None:
            assert isinstance(ksp_G, PETSc.KSP)
            self.ksp_G = ksp_G
        elif self.ksp_G is None:
            self.ksp_G = PETSc.KSP(comm=self.getComm())
            self.ksp_G.setType(PETSc.KSP.Type.GMRES)
            self.ksp_G.getPC().setType(PETSc.PC.Type.NONE)
        # Schur complement operator
        matsc = MatSC(self.domain, self.ksp_L)
        msize = matsc.getSizes()
        mcomm = matsc.getComm()
        self.mat_S = PETSc.MatShell(msize, matsc, comm=mcomm)
        self.vec_b, self.vec_x = self.mat_S.getVecs()
            
        self._setup = False
        
    def getComm(self):
        return self.domain.getComm()

    def getDomain(self):
        return self.domain

    def getLocalSolver(self):
        return self.ksp_L

    def getGlobalSolver(self):
        return self.ksp_G

    def getMatrix(self):
        if self.mat_A is None:
            raise ValueError('matrix not set')
        return self.mat_A, self.str_A
    
    def setMatrix(self, matrix, structure=None):
        assert isinstance(matrix, PETSc.Mat)
        self.mat_A = matrix
        if structure is None:
            structure = PETSc.Mat.Structure.DIFFERENT_NONZERO_PATTERN
        self.str_A = structure
        self._setup = False
        
    def setUp(self):
        if self._setup: return
        # --------------------
        mat_A, str_A = self.getMatrix()
        same_nz = PETSc.Mat.Structure.SAME_NONZERO_PATTERN
        reuse = bool(str_A == same_nz)
        self.mat_S.getShellContext().setMatrix(mat_A, reuse)
        ksp_G = self.getGlobalSolver()
        ksp_G.setOperators(self.mat_S, self.mat_S, same_nz)
        # --------------------
        self._setup = True
    
    def solve(self, b, x):
        self.setUp()
        bG, xG = self.vec_b, self.vec_x
        ksp_G  = self.getGlobalSolver()
        schur  = self.mat_S.getShellContext()
        if ksp_G.getInitialGuessNonzero():
            schur.buildGuess(x, xG)
        schur.buildRhs(b, bG)
        ksp_G.solve(bG, xG)
        schur.buildSolution(xG, b, x)




class MatB(object):

    def __init__(self, dom, A_BB):
        self.domain = dom
        self.A_BB = A_BB
        self.u_B, self.v_B = A_BB.getVecs()

    def getDiagonal(self, d):
        self.A_BB.getDiagonal(self.u_B)
        d.zeroEntries()
        self.domain.scatter(self.u_B, d)
        
    def mult(self, x, y):
        u_B, v_B = self.u_B, self.v_B
        y.zeroEntries()
        self.domain.gather(x, u_B)
        self.A_BB.mult(u_B, v_B)
        self.domain.scatter(v_B, y)
        
    

class PCB(object):

    def __init__(self, ksp_B):
        self.ksp_B = ksp_B
        
    def preSolve(self, ksp, b, x):
        S, _, _ = ksp.getOperators()
        schur = S.getContext()
        dom  = schur.getDomain()
        A_BB = schur.getSubMatrices()[3]
        shell = MatB(dom, A_BB)
        msize = schur.getSizes()
        mcomm = schur.getComm()
        MS = PETSc.MatShell(msize, shell, mcomm)
        self.MS = MS
        self.ksp_B.setOperators(MS, MS)
        
    def apply(self, x, y):
        self.ksp_B.solve(x, y)


class PCB2(object):

    def __init__(self, ksp_B):
        pass

    def preSolve(self, ksp, b, x):
        S, _, _ = ksp.getOperators()
        schur = S.getContext()
        dom  = schur.getDomain()
        A_BB = schur.getSubMatrices()[3]
        self.ksp_B = PETSc.KSP('preonly', 'lu', comm=A_BB.comm)
        same_nz = PETSc.PC.Structure.SAME_NONZERO_PATTERN
        self.ksp_B.setOperators(A_BB, A_BB, same_nz)
        self.domain = dom
        self.u_B, self.v_B = A_BB.getVecs()
        
    def apply(self, x, y):
        u_B, v_B = self.u_B, self.v_B
        y.zeroEntries()
        self.domain.gather(x, u_B)
        self.ksp_B.solve(u_B, v_B)
        self.domain.scatter(v_B, y)

# ---------------------------------------------------

def Poisson3D(H, gridshape):
 
    nnods  = array.product(gridshape)
    n0, n1, n2 = gridshape
    e0, e1, e2 = n0-1, n1-1, n2-1

    nodes = array.arange(n0*n1*n2, dtype=PETSc.Int).reshape(n0, n1, n2)

    icone = array.zeros((e0,e1,e2, 8))
    icone[:,:,:,0] = nodes[ 0:n0-1 , 0:n1-1, 0:n2-1 ]
    icone[:,:,:,1] = nodes[ 1:n0   , 0:n1-1, 0:n2-1 ]
    icone[:,:,:,2] = nodes[ 1:n0   , 1:n1  , 0:n2-1 ]
    icone[:,:,:,3] = nodes[ 0:n0-1 , 1:n1  , 0:n2-1 ]
    icone[:,:,:,4] = nodes[ 0:n0-1 , 0:n1-1, 1:n2   ]
    icone[:,:,:,5] = nodes[ 1:n0   , 0:n1-1, 1:n2   ]
    icone[:,:,:,6] = nodes[ 1:n0   , 1:n1  , 1:n2   ]
    icone[:,:,:,7] = nodes[ 0:n0-1 , 1:n1  , 1:n2   ]
    icone.shape = (e0*e1*e2, 8)
    icone = icone[:, [4,5,6,7,0,1,2,3]]

    elmat = [[ 4,  0, -1,  0,  0, -1, -1, -1],
             [ 0,  4,  0, -1, -1,  0, -1, -1],
             [-1,  0,  4,  0, -1, -1,  0, -1],
             [ 0, -1,  0,  4, -1, -1, -1,  0],
             [ 0, -1, -1, -1,  4,  0, -1,  0],
             [-1,  0, -1, -1,  0,  4,  0, -1],
             [-1, -1,  0, -1, -1,  0,  4,  0],
             [-1, -1, -1,  0,  0, -1,  0,  4]]
    elvec = [1] * 8

    elmat = 1.0/(12*H) * array.array(elmat, dtype=PETSc.Scalar)
    elvec = 1.0/8      * array.array(elvec, dtype=PETSc.Scalar)

    nnod = nodes.size
    A = PETSc.MatSeqAIJ(nnods, nz=27)
    x, b = A.getVecs()
    ADD_VALUES = PETSc.InsertMode.ADD_VALUES
    A_setValues = A.setValues
    b_setValues = b.setValues
    for elem in icone:
        A_setValues(elem, elem, elmat, ADD_VALUES)
        b_setValues(elem,       elvec, ADD_VALUES)
    A.assemble()
    b.assemble()
    return A, b, x


def Poisson2D(H, gridshape):
    
    nnods  = array.product(gridshape)
    n0, n1 = gridshape
    e0, e1 = n0-1, n1-1

    nodes = array.arange(nnods, dtype=PETSc.Int).reshape(n0, n1)
    
    icone = array.zeros((e0,e1,4))
    icone[:,:, 0] = nodes[ 0:n0-1 , 0:n1-1 ]
    icone[:,:, 1] = nodes[ 1:n0   , 0:n1-1 ]
    icone[:,:, 2] = nodes[ 1:n0   , 1:n1   ]
    icone[:,:, 3] = nodes[ 0:n0-1 , 1:n1   ]
    icone.shape = (e0*e1,4)

    elmat =[[  2,   -0.5, -1,   -0.5 ],
            [ -0.5,  2,   -0.5, -1   ],
            [ -1,   -0.5,  2,   -0.5 ],
            [ -0.5, -1,   -0.5,  2   ]]    
    elvec = [1, 1, 1, 1]

    elmat = 1.0/(3*H) * array.array(elmat, dtype=PETSc.Scalar)
    elvec = 1.0/4     * array.array(elvec, dtype=PETSc.Scalar) 

    A = PETSc.MatSeqAIJ(nnods, nz=9)
    x, b = A.getVecs()
    ADD_VALUES = PETSc.InsertMode.ADD_VALUES
    A_setValues = A.setValues
    b_setValues = b.setValues
    for elem in icone:
        A_setValues(elem, elem, elmat, ADD_VALUES)
        b_setValues(elem,       elvec, ADD_VALUES)
    A.assemble()
    b.assemble()

    return A, b, x


if __name__ != '__main__':
    import sys
    sys.exit(0)

import numpy.core as array

size = PETSc.WORLD_SIZE
rank = PETSc.WORLD_RANK


COMM = PETSc.COMM_WORLD

NDIM  = 3

SHAPE = 3, 3, 3
#HAPE = 5, 5, 5
SHAPE = 10, 10, 10
#SHAPE = 20, 20, 20
#SHAPE = 30, 30, 30
#SHAPE = 30, 30, 30

PART  = 2, 2, 2
BBOX = [(0.0, 1.0)] * 3

h =[(bb[1]-bb[0])/(SHAPE[i]-1)
    for i,bb in enumerate(BBOX)]
H = array.product(h)

from Grid import Grid
grid = Grid(SHAPE, bbox=BBOX, part=PART, pid=rank)

snodes = grid.nodes

A, b, x = Poisson3D(H, snodes.shape)
#bnd = array.concatenate(grid.boundary).astype(PETSc.Int)
#val = array.zeros(bnd.size).astype(PETSc.Scalar)
#A.zeroRows(bnd)
#b.setValues(bnd, val)
if rank==0:
    A.zeroRows(0)
    b.setValues(0, 0)

lgmap = PETSc.LGMapping(snodes, comm=COMM)

ksp_L = PETSc.KSP(ksp_type='preonly', pc_type='lu',   comm=PETSc.COMM_SELF)
ksp_G = PETSc.KSP(ksp_type='cg',      pc_type='none', comm=COMM)

#sp_G.pc.type = 'jacobi'

ksp_L.setFromOptions()
ksp_G.setFromOptions()
ksp_G.guess_nonzero = True
ksp_G.max_it = 50

solver = Solver(lgmap, ksp_L, ksp_G)
same_nz = PETSc.Mat.Structure.SAME_NONZERO_PATTERN
solver.setMatrix(A, same_nz)

#ksp_B = PETSc.KSP(ksp_type='richardson', pc_type='jacobi')
#ksp_B.setOptionsPrefix('pcb_')
#ksp_B.setFromOptions()
#ksp_B.max_it = 10
#pc = PCB(ksp_B)
#pc = PCB2(ksp_B)
#pcshell = PETSc.PCShell(pc)
#ksp_G.setPC(pcshell)

from time import time

x.set(0)
t = time()
solver.solve(b, x)
t = time()-t

PETSc.Print('its:%d,  time: %f\n'% (ksp_G.iternum, t))

x.set(0)
t = time()
solver.solve(b, x)
t = time()-t

PETSc.Print('its:%d,  time: %f\n'% (ksp_G.iternum, t))


x.set(0)
t = time()
solver.solve(b, x)
t = time()-t

PETSc.Print('its:%d,  time: %f\n'% (ksp_G.iternum, t))


#x.view()
#vwd = PETSc.ViewerDraw()
#vwd(x)
#pcsc.schur.D.view()

def dealloc():
    global A, b, x, lgmap, ksp_L, ksp_G, solver
    del A, b, x, lgmap, ksp_L, ksp_G, solver

#vwg = PETSc.ViewerDraw(comm=PETSc.COMM_SELF)
#vwg(x)

loops = 5
if loops:
    PETSc.Print('---------------------------\n')
for i in xrange(loops):
    #A.getLocalMat().scale(2)
    #print A.getLocalMat().norm()
    #same_nz = PETSc.Mat.Structure.SAME_NONZERO_PATTERN
    #ksp.setOperators(A, A, same_nz)
    x.set(0)
    solver.solve(b, x)
    fmt = 'its:%d,  time: %f,  ||x||: %f, min(x): %s, max(x): %s\n'
    args = (solver.ksp_G.iternum, t, x.norm(), x.min(), x.max())
    PETSc.Print(fmt % args)
    
