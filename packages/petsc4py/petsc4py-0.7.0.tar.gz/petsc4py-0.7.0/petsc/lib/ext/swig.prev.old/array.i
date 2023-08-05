/* $Id$ */

/* ---------------------------------------------------------------- */
/* Array object support                                             */
/* ---------------------------------------------------------------- */
/* - NumPy is the supported array object implementation             */
/* ---------------------------------------------------------------- */

/* macros for array handling */

%include numpy.i

/* numeric types and precisions */

%{
#if defined(PETSC_USE_64BIT_INDICES)
# define PyPetscArray_INT     PyArray_LONGLONG
#else
# define PyPetscArray_INT     PyArray_INT
#endif
  
#if defined(PETSC_USE_COMPLEX)
# define PyPetscArray_REAL    PyArray_DOUBLE
# define PyPetscArray_COMPLEX PyArray_CDOUBLE
# define PyPetscArray_SCALAR  PyArray_CDOUBLE
#else
# if   defined(PETSC_USE_SINGLE)
#  define PyPetscArray_REAL    PyArray_FLOAT
#  define PyPetscArray_COMPLEX PyArray_CFLOAT
#  define PyPetscArray_SCALAR  PyArray_FLOAT
# elif defined(PETSC_USE_LONG_DOUBLE)
#  define PyPetscArray_REAL    PyArray_LONGDOUBLE
#  define PyPetscArray_COMPLEX PyArray_CLONGDOUBLE
#  define PyPetscArray_SCALAR  PyArray_LONGDOUBLE
# elif defined(PETSC_USE_INT)
#  define PyPetscArray_REAL    PyArray_INT
#  define PyPetscArray_COMPLEX PyArray_CFLOAT /* ??? */
#  define PyPetscArray_SCALAR  PyArray_INT
# else      /* PETSC_USE_DOUBLE */
#  define PyPetscArray_REAL    PyArray_DOUBLE
#  define PyPetscArray_COMPLEX PyArray_CDOUBLE
#  define PyPetscArray_SCALAR  PyArray_DOUBLE
# endif
#endif
%}

ARRAY_NUMTYPE(PetscInt,     PyPetsc_INT,     PyPetscArray_INT)
ARRAY_NUMTYPE(PetscReal,    PyPetsc_REAL,    PyPetscArray_REAL)
ARRAY_NUMTYPE(PetscComplex, PyPetsc_COMPLEX, PyPetscArray_COMPLEX)
ARRAY_NUMTYPE(PetscScalar,  PyPetsc_SCALAR,  PyPetscArray_SCALAR)


/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
