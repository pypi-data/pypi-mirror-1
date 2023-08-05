import petsc.PETSc as PETSc


print
print "Using 'NullSpace' objects"
print '========================='
print


print 'Original Basis'
print '--------------'
u1 = PETSc.Vec.CreateSeq(3); u1.name = 'u1'; u1.array = [1,  2, 0]
u2 = PETSc.Vec.CreateSeq(3); u2.name = 'u2'; u2.array = [2, -1, 0]
print '%s: %s - |%s|: %f' % (u1.name, u1.array, u1.name, u1.normalize())
print '%s: %s - |%s|: %f' % (u2.name, u2.array, u2.name, u2.normalize())
print


print 'Orthonormal Basis'
print '-----------------'
print '%s: %s' % (u1.name, u1.array)
print '%s: %s' % (u2.name, u2.array)
print '<%s,%s>: %f' % (u1.name, u1.name, u1.dot(u1))
print '<%s,%s>: %f' % (u1.name, u2.name, u1.dot(u2))
print '<%s,%s>: %f' % (u2.name, u2.name, u2.dot(u2))
print


print 'Null Space, N = span{u1,u2}'
print '---------------------------'
nullsp = PETSc.NullSpace.Create([u1,u2])
nullsp.name = 'N'
print 'N = PETSc.NullSpace([u1,u2])'
print 


print 'Vector before removal'
print '---------------------'
v = PETSc.Vec.CreateSeq(3); v.name = 'v'
v.array = [7,  8, 9]
print '%s : %s' % (v.name, v.array)
print

print 'Vector after removal'
print '--------------------'
w = v.duplicate(); w.name = 'w'
nullsp.remove(v, w)
print '%s : %s' % (w.name, w.array)
print

print 'Inplace removal'
print '--------------------'
nullsp.remove(v)
print '%s : %s' % (v.name, v.array)
print


print 'Destroying objects ...'
for o in (nullsp, u1, u2, v, w):
    print o.name
    o.destroy()
del nullsp, u1, u2, v, w, o

print

