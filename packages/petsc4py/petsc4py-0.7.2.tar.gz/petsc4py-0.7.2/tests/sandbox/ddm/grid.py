import petsc.PETSc as PETSc
import numpy.core  as array


class GridSeq(object):
    
    def __init__(self, shape, bbox):

        assert len(shape) == len(bbox)
        shape = tuple(int(i) for i in shape)
        bbox = tuple((float(i), float(j)) for i,j in bbox)

        # nodes
        ndim = len(shape)
        nnod = array.product(shape)
        nodes = array.arange(nnod).reshape(shape)
        # coordinates
        axes = tuple(slice(bb[0], bb[1], shape[i]*1j)
                     for i, bb in enumerate(bbox))
        xnod = array.mgrid[axes].reshape(ndim, nnod)
        xnod = xnod.transpose().copy()
        xnod[:,[0,-1]] = xnod[:,[-1,0]].copy()
        xnod = xnod.reshape(shape+(ndim,))
        
        self.ndim  = ndim
        self.nnod  = nnod
        self.shape = shape
        self.bbox  = bbox
        self.xnod  = xnod
        self.nodes = nodes
        

def subgrid(shape, nbox):
    pass
    

class mesh(object):
    def __init__(self, grid):
        pass

g = GridSeq([2,2,2], [[0,1]]*3)
