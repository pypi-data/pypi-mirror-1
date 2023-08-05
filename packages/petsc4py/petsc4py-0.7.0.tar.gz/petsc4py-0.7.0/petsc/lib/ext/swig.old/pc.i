/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode 
PCCreate(MPI_Comm, PC* CREATE);

/* ---------------------------------------------------------------- */

%wrapper %{
#define PCSetOperators(pc, A, P, matstr) \
        PCSetOperators(pc, A, (P==PETSC_NULL)?A:P, matstr)
%}

PetscErrorCode
PCGetOperators(PC, Mat* NEWREF, Mat* NEWREF, MatStructure*);

PetscErrorCode
PCSetOperators(PC, Mat, Mat OBJ_OR_NONE, MatStructure);

PetscErrorCode
PCGetOperatorsSet(PC, PetscTruth *mat, PetscTruth *pmat);

PetscErrorCode
PCComputeExplicitOperator(PC, Mat* NEWOBJ);

/* ---------------------------------------------------------------- */

%typemap(in, numinputs=0, noblock=1) (PetscInt* n, KSP* ksp[])
(KSP temp=PETSC_NULL, $*1_ltype n_ksp=0, $*2_ltype ksp)
{ksp = &temp; $1 = &n_ksp; $2 = &ksp;}
%typemap(argout) (PetscInt* n, KSP* ksp[])
{ int i; for(i=0;i<*$1;i++) %append_output(PyKSP_Ref((*$2)[i])); };

PETSC_OVERRIDE(
PetscErrorCode,
PCGetSubKSP,
(PC pc, PetscInt* n, KSP* ksp[]), {
  PetscErrorCode ierr;
  PetscTruth     flg;
  PetscFunctionBegin;
  *n = 0; *ksp = 0;
  ierr = PetscTypeCompare((PetscObject)pc,PCBJACOBI,&flg);CHKERRQ(ierr);
  if (flg) { ierr = PCBJacobiGetSubKSP(pc,n,PETSC_NULL,ksp);CHKERRQ(ierr); goto done; }
  ierr = PetscTypeCompare((PetscObject)pc,PCASM,&flg);CHKERRQ(ierr);
  if (flg) { ierr = PCASMGetSubKSP(pc,n,PETSC_NULL,ksp);CHKERRQ(ierr);     goto done; }
  ierr = PetscTypeCompare((PetscObject)pc,PCKSP,&flg);CHKERRQ(ierr);
  if (flg) { *n = 1; ierr = PCKSPGetKSP(pc,&((*ksp)[0]));CHKERRQ(ierr);    goto done; }
  ierr = PetscTypeCompare((PetscObject)pc,PCSCHUR,&flg);CHKERRQ(ierr);
  if (flg) { ierr = PCSchurGetSubKSP(pc,n,ksp);CHKERRQ(ierr);      goto done; }
  SETERRQ(PETSC_ERR_ARG_WRONG,"Cannot get subsolvers from this preconditioner");
 done:
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
