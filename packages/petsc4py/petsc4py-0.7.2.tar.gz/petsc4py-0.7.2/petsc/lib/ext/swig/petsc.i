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

/*
 * Local Variables:
 * mode: C
 * End:
 */
