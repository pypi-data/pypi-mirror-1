import petsc.PETSc as PETSc

opts = dict(zip('a b c'.split(), [0, 1, 2]))
for k in opts:
    PETSc.Options.SetValue(k, opts[k])
PETSc.Options.Print()
for opt in 'a b c'.split():
    print "has opt '%s': %s" % (opt, PETSc.Options.HasName(opt))
print

prefix = 'with-prefix-'
opts = PETSc.Options(prefix)
opts['x'] = 0.0
opts['y'] = 1.0
opts['z'] = 2.0
PETSc.Options.Print()
for name in 'x y z'.split():
    print "has opt '%s%s': %s" % \
          (prefix, name, PETSc.Options.HasName(name, prefix))
print

opts['x'] = 'no'
del opts['y']
del opts['z']
PETSc.Options.Print()
for name in 'x y z'.split():
    print "has opt '%s%s': %s" % \
          (prefix, name, PETSc.Options.HasName(name, prefix))
print

del opts

print 'global opts remaining:', PETSc.Options.GetAll()
