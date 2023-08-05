import unittest, os, tempfile

# --------------------------------------------------------------------

class TestImport(unittest.TestCase):

    def setUp(self):
        import petsc4py.lib
        petscext = petsc4py.lib.Import()
        dname = os.path.dirname(petscext.__file__)
        arch = os.path.split(dname)[-1]
        self.petscext = petscext
        self.arch = arch

    def testNotInited(self):
        is_inited  = getattr(self.petscext, 'PetscInitialized', None)
        is_finited = getattr(self.petscext, 'PetscFinalized', None)
        if is_inited:
            self.assertFalse(is_inited())
        if is_finited:
            self.assertFalse(is_finited())

    def testImport(self):
        import petsc4py.lib
        petscext = petsc4py.lib.Import()
        self.assertTrue(self.petscext is petscext)
        self.testNotInited()

    def testImportArch(self):
        import petsc4py.lib
        petscext = petsc4py.lib.Import(self.arch)
        def _test():
            petsc4py.lib.Import(tempfile.mktemp(dir=''))
        self.assertRaises(ImportError, _test)
        self.testNotInited()

    def testInit(self):
        import petsc4py as petsc
        petsc.init()
        self.testNotInited()

    def testInitArgs(self):
        import petsc4py as petsc
        petsc.init([])
        self.testNotInited()

    def testInitArgsArch(self):
        import petsc4py as petsc
        petsc.init([], self.arch)
        def _test():
            petsc.init(arch=tempfile.mktemp(dir=''))
        self.assertRaises(ImportError, _test)
        self.testNotInited()
        
    def testInitArgsArchComm(self):
        import petsc4py as petsc
        petsc.init([], self.arch, comm=None)
        self.testNotInited()
       
# --------------------------------------------------------------------

if __name__ == '__main__':

    def init():
        from petsc4py import PETSc
    import atexit
    atexit.register(init)
    del init, atexit

    unittest.main()
    
