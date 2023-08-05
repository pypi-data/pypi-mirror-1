/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Function                                                */
/* ---------------------------------------------------------------- */

PetscErrorCode PetscRandomCreate(MPI_Comm comm, PetscRandom* CREATE);
%ignore PetscRandomCreate;

/* ---------------------------------------------------------------- */

%apply unsigned long *OUTPUT { unsigned long *seed };
PetscErrorCode PetscRandomGetSeed(PetscRandom, unsigned long *seed);
%clear unsigned long *seed;

%ignore PetscRandomGetSeed;

/* ---------------------------------------------------------------- */

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


