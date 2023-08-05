/* $Id$ */

#if SWIG_VERSION < 0x010330
%warn "SWIG version < 1.3.30, not tested!!"
#endif

/* Include PETSc headers in wrapper file */
%{
#include <petsc.h>
#include <petscis.h>
#include <petscao.h>
#include <petscvec.h>
#include <petscmat.h>
#include <petscksp.h>
#include <petscsnes.h>
#include <petscts.h>
%}

%include forward.i
%include ignore.i
%include macros.i

/* Specific interface files */

%include error.i

%include commtype.i
%include objtype.i
%include tpmaps.i
%include array.i
%include context.i
%include ctorreg.i

%include objinit.i

%include sys/sys.i

%include dm/ao.i

%include vec/is/is.i
%include vec/vec/vec.i

%include mat/mat.i

%include ksp/ksp/ksp.i
%include ksp/pc/pc.i

%include snes/snes.i

%include ts/ts.i


/* Feed SWIG with PETSc configuration */

%PETSC_CONFIG(PETSC_DIR, PETSC_ARCH)

//#if !defined(__cplusplus)
//#  if defined(PETSC_CLANGUAGE_CXX) && !defined(PETSC_USE_EXTERN_CXX)
//#    undef PETSC_CLANGUAGE_CXX
//#  endif
//#endif


///* Feed SWIG with PETSc headers */
//%PETSC_HEADER(PETSC_DIR, petsc.h)
//#if defined(__cplusplus) && !defined(PETSC_USE_EXTERN_CXX)
//# undef  PetscPolymorphicSubroutine
//# undef  PetscPolymorphicScalar
//# undef  PetscPolymorphicFunction
//# define PetscPolymorphicSubroutine(A,B,C)
//# define PetscPolymorphicScalar(A,B,C)
//# define PetscPolymorphicFunction(A,B,C,D,E)
//#endif

//%PETSC_HEADER(PETSC_DIR, petscsys.h);
//%PETSC_HEADER(PETSC_DIR, petscviewer.h);
//%PETSC_HEADER(PETSC_DIR, petscis.h);
//%PETSC_HEADER(PETSC_DIR, petscao.h);
//%PETSC_HEADER(PETSC_DIR, petscvec.h);
//%PETSC_HEADER(PETSC_DIR, petscmat.h);
//%PETSC_HEADER(PETSC_DIR, petscpc.h);
//%PETSC_HEADER(PETSC_DIR, petscksp.h);
//%PETSC_HEADER(PETSC_DIR, petscsnes.h);
//%PETSC_HEADER(PETSC_DIR, petscts.h);



/*
 * Local Variables:
 * mode: C
 * End:
 */
