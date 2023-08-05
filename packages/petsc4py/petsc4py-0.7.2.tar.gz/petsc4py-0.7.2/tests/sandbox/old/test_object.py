import petsc.PETSc as PETSc
from sys import getrefcount

def refcnt(o):
    return getrefcount(o) - 3
#refcnt = getrefcount

u = PETSc.Vec.CreateSeq(10)
print 'u = PETSc.VecSeq(2)'
print 'u.owner:'   , u.owner
print 'refcnt(u):' , refcnt(u)


v = PETSc.Vec.CreateSeq(u)
print
print 'v = PETSc.VecSeq(u)'
print 'u is v:'    , u is v
print 'u == v:'    , u == v
print 'v.owner:'   , v.owner
print 'refcnt(v):' , refcnt(v)


w = PETSc.Vec(u)
print
print 'w = PETSc.Vec(u)'
print 'u is w:'   , u is w
print 'u == w:'   , u == w
print 'w.owner:'  , w.owner 
print 'refcnt(w):', refcnt(w)


x = PETSc.Vec(w)
print
print 'x = PETSc.Vec(w)'
print 'x is w:'   , x is w
print 'x == w:'   , x == w
print 'x.owner:'  , x.owner 
print 'refcnt(x):', refcnt(x)



try:
    print
    print 'o = PETSc.Object(u)'
    o = PETSc.Object(u)
except TypeError, e:
    print e

try:
    print
    print 'o = PETSc.Vec(u)'
    o = PETSc.Vec(u)
except TypeError, e:
    print '%s: %s' % (TypeError, e)

try:
    print
    print 'o = PETSc.VecSeq(u)'
    o = PETSc.VecSeq(u)
except TypeError, e:
    print '%s: %s' % (TypeError, e)


try:
    print
    print 'o = PETSc.VecMPI(u)'
    o = PETSc.VecMPI(w)
except TypeError, e:
    print '%s: %s' % (TypeError, e)

try:
    print
    print 'o = PETSc.Mat(u)'
    o = PETSc.Mat(w)
except TypeError, e:
    print '%s: %s' % (TypeError, e)


del v, w, x, o
print
print 'del v, w, x, o'
print 'bool(u):'   , bool(u)
print 'u.valid:'   , u.valid
print 'u.size:'    , u.size
print 'u.owner:'   , u.owner
print 'refcnt(u):' , refcnt(u)
