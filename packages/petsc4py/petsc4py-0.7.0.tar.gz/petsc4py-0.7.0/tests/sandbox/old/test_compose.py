from petsc.PETSc import *

o1 = Vec.CreateSeq(0)
o1.name = 'obj1'

o2 = Vec.CreateSeq(0)
o2.name = 'obj2'

o1.compose('o2', o2)
assert o1.refcount == 1
assert o2.refcount == 2

oo1 = o1.query('o1')
assert oo1 is None
oo2 = o1.query('o2')
assert oo2 is not None


o1.compose('o2', None)
assert o1.refcount == 1
assert o2.refcount == 1


oo1 = o1.query('o1')
assert oo1 is None
oo2 = o1.query('o2')
assert oo2 is None
