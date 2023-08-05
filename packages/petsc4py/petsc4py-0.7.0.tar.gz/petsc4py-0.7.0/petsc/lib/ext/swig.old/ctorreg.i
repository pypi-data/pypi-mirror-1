/* ---------------------------------------------------------------- */

%wrapper %{
EXTERN_C_BEGIN
EXTERN PetscErrorCode PETSCMAT_DLLEXPORT MatCreate_ISX(Mat A);
EXTERN_C_END
%}

/* ---------------------------------------------------------------- */

#define PCSCHUR  "schur"

%wrapper %{
#define PCSCHUR  "schur"
EXTERN_C_BEGIN
EXTERN PetscErrorCode PETSCKSP_DLLEXPORT PCCreate_Schur(PC);
EXTERN_C_END
%}

#define PCNSI  "nsi"

%wrapper %{
#define PCNSI  "nsi"
EXTERN_C_BEGIN
/*EXTERN PetscErrorCode PETSCKSP_DLLEXPORT PCCreate_NSI(PC);*/
EXTERN_C_END
%}

/* ---------------------------------------------------------------- */

#define TS_USER  "user"

%wrapper %{
#define TS_USER  "user"
EXTERN_C_BEGIN
EXTERN PetscErrorCode PETSCTS_DLLEXPORT TSCreate_User(TS);
EXTERN_C_END
%}


/* ---------------------------------------------------------------- */

%wrapper %{
#undef  __FUNCT__  
#define __FUNCT__ "PyPetscRegisterAll"
static PetscErrorCode
PyPetscRegisterAll(const char path[]) {
  PetscErrorCode ierr;
  PetscFunctionBegin;
#ifndef PETSC_USE_DYNAMIC_LIBRARIES
  ierr = MatInitializePackage(PETSC_NULL);CHKERRQ(ierr);
#endif
  ierr = MatRegisterDynamic (MATIS,   path, "MatCreate_ISX",  MatCreate_ISX);  CHKERRQ(ierr);
#ifndef PETSC_USE_DYNAMIC_LIBRARIES
  ierr = PCInitializePackage(PETSC_NULL);CHKERRQ(ierr);
#endif
  ierr = PCRegisterDynamic  (PCSCHUR, path, "PCCreate_Schur", PCCreate_Schur); CHKERRQ(ierr);
  /*ierr = PCRegisterDynamic  (PCNSI,   path, "PCCreate_NSI",   PCCreate_NSI);   CHKERRQ(ierr);*/
#ifndef PETSC_USE_DYNAMIC_LIBRARIES
  ierr = TSInitializePackage(PETSC_NULL);CHKERRQ(ierr);
#endif
  ierr = TSRegisterDynamic(TS_USER,   path, "TSCreate_User",  TSCreate_User);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
%}

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
