import numpy.core as array

def strides(shape):
    stride = [1] + list(reversed(shape))
    stride = array.cumproduct(stride)
    stride = list(reversed(stride))[1:]
    return stride
    
def crd2idx(coord, shape):
    index = 0
    for i, stride in enumerate(strides(shape)):
        index += coord[i] * stride
    return index

def idx2crd(index, shape):
    coord = []
    i = index + 0
    for s in reversed(shape):
        c = i % s
        i -= c
        i /= s
        coord.insert(0, c)
    return tuple(coord)

def linspace(n, d1=0.0, d2=1.0):
    """
    """
    assert n > 1
    lsp  = array.arange(n, dtype=array.Float)
    lsp *= (d2-d1)/(lsp[-1]-lsp[0])
    lsp += d1
    return lsp

def meshgrid(*axes):
    """
    """
    indices = array.indices([len(axis) for axis in axes])
    axes = tuple(array.array(axes[i])[index]
                 for i, index in enumerate(indices))
    return axes

def make_grid(shape, axes=None):
    if axes is None:
        return array.arange(array.product(shape), shape=shape)
    axes = [array.array(axis) for axis in axes]
    sizes = [axis.size for axis in axes]
    axes = meshgrid(*axes)
    nodes = crd2idx(axes, shape)
    nodes.shape = sizes
    return nodes

def make_hexa(nodes):
    assert len(nodes.shape) == 3
    n0, n1, n2 = nodes.shape
    e0, e1, e2 = (n-1 for n in nodes.shape)
    icone = array.zeros(shape=(e0, e1, e2, 8))
    # front face
    icone[...,0] = nodes[ 0:n0-1 , 0:n1-1, 0:n2-1 ]
    icone[...,1] = nodes[ 0:n0-1 , 0:n1-1, 1:n2   ]
    icone[...,2] = nodes[ 0:n0-1 , 1:n1  , 1:n2   ]
    icone[...,3] = nodes[ 0:n0-1 , 1:n1  , 0:n2-1 ]
    # back face
    icone[...,4] = nodes[ 1:n0   , 0:n1-1, 0:n2-1 ]
    icone[...,5] = nodes[ 1:n0   , 0:n1-1, 1:n2   ]
    icone[...,6] = nodes[ 1:n0   , 1:n1  , 1:n2   ]
    icone[...,7] = nodes[ 1:n0   , 1:n1  , 0:n2-1 ]
    # final mesh
    icone.shape = (e0*e1*e2, 8)
    return icone

def make_tetra(hexas):
    hexas = array.array(hexas)
    assert len(hexas.shape) == 2
    assert hexas.shape[1] == 8
    part = [0, 1, 3, 4,
            2, 5, 6, 7,
            3, 4, 5, 7,
            3, 5, 2, 7,
            3, 1, 2, 5,
            3, 4, 1, 5]
    tetras = array.take(hexas, part, axis=1)
    shape  = (hexas.shape[0]*6, 4)
    return array.reshape(tetras, shape)


## def split_ownership(i, bins, gsize):
##     lsize = gsize/bins + (gsize % bins > i)
##     return lsize

def range_ownership(i, bins, gsize, overlap=False):
    lsizes = gsize/bins + (gsize % bins > array.arange(bins))
    ranges = array.zeros(len(lsizes)+1)
    ranges[1:] = array.cumsum(lsizes)
    rng = [ranges[i], ranges[i+1]]
    if overlap and i > 0:
        rng[0]-=1
    return tuple(rng)
    


class Partition:
    
    """
    Partition for structured grids
    """
    
    def __init__(self, shape=1, index=0):
        """
        shape: global partition shape.
        index: global partition index.
        """
        if shape is None:
            shape = (1,)
        elif isinstance(shape, int):
            shape = (shape,)
        else:
            for s in shape:
                assert isinstance(s, int)
            shape = tuple(shape)

        if index is None:
            index = 0
        else:
            assert isinstance(index, int)
            assert index < array.product(shape)
        
        self.ndim  = len(shape)
        self.shape = shape
        self.size  = array.product(shape)
        self.index = index
        self.coord = idx2crd(index, shape)

    def split_ownership(self, gshape, overlap=True):
        assert len(gshape) == self.ndim
        lshape = list(gshape[i]/p + (gshape[i] % p > self.coord[i])
                      for i, p in enumerate(self.shape))
        if overlap:
            for i, c in enumerate(self.coord):
                if c > 0:
                    lshape[i] += 1
        lshape = tuple(lshape)
        return lshape
        
    def ownership_range(self, gshape, overlap=True):
        assert len(gshape) == self.ndim
        ownrng = []
        for i, p in enumerate(self.coord):
            bins  = self.shape[i]
            gsize = gshape[i]
            lsizes = gsize/bins + (gsize % bins > array.arange(bins))
            ranges = array.zeros(len(lsizes)+1)
            ranges[1:] = array.cumsum(lsizes).astype(ranges.dtype)
            rng = [ranges[p], ranges[p+1]]
            if overlap and p > 0:
                rng[0]-=1
            ownrng.append(tuple(rng))
        return ownrng


class Grid:

    """
    Structured grid
    """
    
    def __init__(self, shape, bbox=None, part=None, pid=None):

        ndim = len(shape)
        if bbox is None:
            bbox = ((0,1), ) * ndim
        else:
            assert len(bbox) == ndim
            for b in bbox:
                assert len(b) == 2
                assert b[0] < b[1]
            bbox = tuple(tuple(float(b) for b in bb) for bb in bbox)
            
        if part is None:
            part = (1,) * ndim
        else:
            assert len(part) == len(shape)
            assert shape >= part

        if pid is None:
            pid = 0
        else:
            assert pid < array.product(part)
            
        self.ndim  = len(shape)
        self.size  = array.product(shape)
        self.shape = shape
        self.bbox  = bbox

        self.partition = Partition(part, pid)
        
        self.axes      = self.__make_axes()
        self.nodes     = self.__make_grid()
        self.positions = self.__make_posit()
        self.boundary  = self.__make_boundary()

    def __make_axes(self):
        ranges = self.partition.ownership_range(self.shape, overlap=True)
        axes = tuple(array.arange(*rng) for rng in ranges)
        return axes

    def __make_posit(self):
        posit = [linspace(self.shape[i], bbox[0], bbox[1])
                 for i, bbox in enumerate(self.bbox)]
        posit = [posit[i][axis] for i, axis in enumerate(self.axes)]
        posit = meshgrid(*posit)
        aux = posit
        posit = array.empty(aux[0].shape + (self.ndim,),
                            dtype=array.Float)
        for i, x in enumerate(aux):
            posit[...,i] = x
        return posit
 
    def __make_grid(self):
        return make_grid(self.shape, self.axes)

    def __make_boundary(self):
        boundary = []
        for i in xrange(self.ndim):
            if self.partition.coord[i] == 0:
                bnd = array.take(self.nodes, (0,), axis=i)
            else:
                bnd = array.array([])
            boundary.append(bnd.reshape(bnd.size).copy())
            if self.partition.coord[i] == self.partition.shape[i]-1:
                bnd = array.take(self.nodes, (-1,), axis=i)
            else:
                bnd = array.array([])
            boundary.append(bnd.reshape(bnd.size).copy())
        return boundary


class Mesh3D:

    def __init__(self, grid):
        assert grid.ndim == 3
        self.grid = grid
        self.elements = None


class HexaMesh(Mesh3D):

    def __init__(self, grid):
        Mesh3D.__init__(self, grid)
        self.elements = self.__make_hexa()

    def __make_hexa(self):
        return make_hexa(self.grid.nodes)
        

class TetraMesh(Mesh3D):

    def __init__(self, grid):
        Mesh3D.__init__(self, grid)
        self.elements = self.__make_tetras()

    def __make_tetras(self):
        hexas = make_hexa(self.grid.nodes)
        nodes = [0, 1, 3, 4,
                 2, 5, 6, 7,
                 3, 4, 5, 7,
                 3, 5, 2, 7,
                 3, 1, 2, 5,
                 3, 4, 1, 5]
        tetras = array.take(hexas, nodes, 1)
        tetras = array.reshape(tetras, (hexas.shape[0]*6, 4))
        return tetras




if __name__ == '__main__':
    pass
    import petsc.PETSc as PETSc
    comm = PETSc.GetCommWorld()
    size = PETSc.GetCommSize(comm)
    rank = PETSc.GetCommRank(comm)

    N = 3, 3, 3
    P = 2, 2, 2
    #P = 1, 1, 1

    BBOX = [(1,2), (3,4), (5,15)]

    part = Partition(P, rank)
    G = Grid(N, bbox=BBOX, part=P, pid=rank)
    M = TetraMesh(G)

    posit = G.positions
    posit = array.reshape(posit, (posit.size/3, 3))
    elems = M.elements

    #posit.tofile('xnod.dat', sep=' ')
    #elems.tofile('icone.dat', sep=' ')

##     PETSc.SequentialPhaseBegin()
##     print rank,  posit
##     PETSc.SequentialPhaseEnd()
##     print
##     import sys
    
##     PETSc.SequentialPhaseBegin()
##     print rank,  elems, elems.shape
##     sys.stdout.flush()
##     PETSc.SequentialPhaseEnd()

