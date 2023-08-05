from petsc4py import PETSc
import unittest
import sys, tempfile

# --------------------------------------------------------------------

class TestFileIO(unittest.TestCase):

    def setUp(self):
        self.fileobj = tempfile.TemporaryFile(mode='w+')
        
    def tearDown(self):
        self.fileobj.flush()
        self.fileobj.close()
        self.fileobj  = None

    def testPrint(self):
        PETSc.SetStdout(self.fileobj)
        PETSc.Print('%d\n' % PETSc.COMM_WORLD.getRank())
        PETSc.SetStdout(sys.stdout)
        if PETSc.COMM_WORLD.getRank() == 0:
            self.fileobj.flush()
            self.fileobj.seek(0)
            self.assertEqual(str(0), self.fileobj.read().strip())

    def testSyncPrint(self):
        world_size = PETSc.COMM_WORLD.getSize()
        world_rank = PETSc.COMM_WORLD.getRank()
        PETSc.SetStdout(self.fileobj)
        PETSc.SyncPrint('%d\n' % world_rank)
        PETSc.SyncFlush()
        PETSc.SetStdout(sys.stdout)
        if world_rank == 0:
            self.fileobj.flush()
            self.fileobj.seek(0)
            lines = self.fileobj.readlines()
            self.assertEqual(len(lines), world_size)
            for rank, line in enumerate(lines):
                self.assertEqual(str(rank), line.strip())

    def testWrite(self):
        world_rank = PETSc.COMM_WORLD.getRank()
        PETSc.Write(self.fileobj, '%d\n' % world_rank)
        if world_rank == 0:
            self.fileobj.flush()
            self.fileobj.seek(0)
            self.assertEqual(str(0), self.fileobj.read().strip())

    def testSyncWrite(self):
        world_size = PETSc.COMM_WORLD.getSize()
        world_rank = PETSc.COMM_WORLD.getRank()
        PETSc.SyncWrite(self.fileobj, '%d\n' % world_rank)
        PETSc.SyncFlush()
        if world_rank == 0:
            self.fileobj.flush()
            self.fileobj.seek(0)
            lines = self.fileobj.readlines()
            self.assertEqual(len(lines), world_size)
            for rank, line in enumerate(lines):
                self.assertEqual(str(rank), line.strip())

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
