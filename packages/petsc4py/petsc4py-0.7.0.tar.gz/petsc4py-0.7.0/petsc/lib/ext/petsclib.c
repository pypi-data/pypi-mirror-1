#define PETSCMAT_DLL
#include "src/mat/impls/is/matis.c"
#undef  PETSCMAT_DLL

#define PETSCKSP_DLL
#include "src/ksp/pc/impls/schur/schur.c"
/*#include "src/ksp/pc/impls/nsi/nsi.c"*/
#undef PETSCKSP_DLL

#define PETSCTS_DLL
#include "src/ts/impls/implicit/user/user.c"
#undef PETSCTS_DLL
