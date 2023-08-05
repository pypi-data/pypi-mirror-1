import unittest
from petsc import PETSc

__all__ = ['InitFini']

class InitFini(unittest.TestCase):
    
    def testInitFini(self):
        assert PETSc.IsInitialized(), 'PETSc should be initialized'
        assert not PETSc.IsFinalized(), 'PETSc should not be finalized'
        try:
            PETSc.Initialize()
        except RuntimeError:
            pass
        else:
            assert False, 'second call to `Initialize()` must throw an exception'
        #
        PETSc.Finalize()
        assert PETSc.IsFinalized(), 'PETSc should be  finalized'
        # Test if a second call to `Finalize()` throws an exception
        try:
            PETSc.Finalize()
        except RuntimeError:
            pass
        else:
            assert 0, 'second call to `Finalize()` must throw an exception'
        # Test if a call to `Initialize()` after `Finalize()` throws
        # an exception
        try:
            PETSc.Initialize()
        except RuntimeError:
            pass
        else:
            assert 0,'`Initialize()` after `Finalize()` must throw an exception'

if __name__ == '__main__':
    unittest.main()
