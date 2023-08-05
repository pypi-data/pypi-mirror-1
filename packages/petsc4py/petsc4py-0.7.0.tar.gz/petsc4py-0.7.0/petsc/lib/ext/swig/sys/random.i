/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode PetscRandomCreate(MPI_Comm comm, PetscRandom* CREATE);
PetscErrorCode PetscRandomDestroy(PetscRandom);

PetscErrorCode PetscRandomSetType(PetscRandom, PetscRandomType);
PetscErrorCode PetscRandomGetType(PetscRandom, PetscRandomType*);
PetscErrorCode PetscRandomSetFromOptions(PetscRandom);
PetscErrorCode PetscRandomView(PetscRandom,PetscViewer);

/* ---------------------------------------------------------------- */

PetscErrorCode PetscRandomGetValue(PetscRandom,PetscScalar*);
PetscErrorCode PetscRandomGetValueReal(PetscRandom,PetscReal*);
PetscErrorCode PetscRandomGetValueImaginary(PetscRandom,PetscScalar*);
PetscErrorCode PetscRandomGetInterval(PetscRandom,PetscScalar*,PetscScalar*);
PetscErrorCode PetscRandomSetInterval(PetscRandom,PetscScalar,PetscScalar);
PetscErrorCode PetscRandomSetSeed(PetscRandom,unsigned long);
PetscErrorCode PetscRandomGetSeed(PetscRandom,unsigned long* OUTPUT);
PetscErrorCode PetscRandomSeed(PetscRandom);

/* ---------------------------------------------------------------- */

%ignore PetscRandomSetType;
%ignore PetscRandomGetType;

%ignore PetscRandomInitializePackage;
%ignore PetscRandomList;
%ignore PetscRandomRegisterAllCalled;
%ignore PetscRandomRegisterAll;
%ignore PetscRandomRegister;
%ignore PetscRandomRegisterDynamic;
%ignore PetscRandomRegisterDestroy;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */


