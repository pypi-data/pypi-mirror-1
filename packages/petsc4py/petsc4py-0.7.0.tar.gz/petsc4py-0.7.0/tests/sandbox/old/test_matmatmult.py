import petsc.PETSc as PETSc

# sizes
m, n = 3, 5

# allocate matrices
A = PETSc.MatSeqAIJ((m, n))
B = PETSc.MatSeqAIJ((n, m))

# Aij = min(i,j); i=1..m, j=1..n
for i in xrange(m):
    for j in xrange(n):
        A[i,j] = min(i,j) + 1
A.assemble()

# Bij = max(i,j); i=1..m, j=1..n
for i in xrange(n):
    for j in xrange(m):
        B[i,j] = max(i,j) + 1
B.assemble()

# C = A * B
C = A.matMult(B)
PETSc.Mat.matMult(A, B, C)

# D = B * A
D = B.matMultSymbolic( A)
PETSc.Mat.matMultNumeric(B, A, D)

# view results
for name, matrix in [('A', A),
                     ('B', B),
                     ('C', D),
                     ('D', D)]:
    print name,':'
    matrix.view()
    print
