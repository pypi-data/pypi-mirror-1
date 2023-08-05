import sys, os, re
import unittest
from petsc4py import PETSc

# --------------------------------------------------------------------

class TestLib(unittest.TestCase):
    
    def testLib(self):
        basedir = os.path.split(PETSc.__file__)[0]
        files = [os.path.join(basedir, f)
                 for f in os.listdir(basedir)
                 if os.path.splitext(f)[1] == '.py']
        libdir = os.path.join(basedir, 'lib')
        files += [os.path.join(libdir, f)
                  for f in os.listdir(libdir)
                  if os.path.splitext(f)[1] == '.py']
        symbols = set()
        regex = re.compile(r'\w+')
        for f in files:
            fd = open(f)
            for line in fd:
                if '_petsc.' in line:
                    bit = line.split('_petsc.')[1]
                    m = regex.match(bit)
                    sym = m.group()
                    symbols.add(sym)
        from petsc4py.lib import _petsc
        for sym in symbols:
            getattr(_petsc, sym)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
