/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode PCCreate(MPI_Comm, PC* CREATE);
PetscErrorCode PCDestroy(PC);
PetscErrorCode PCView(PC,PetscViewer);

PetscErrorCode PCSetType(PC,PCType);
PetscErrorCode PCGetType(PC,PCType*);

PetscErrorCode PCSetOptionsPrefix(PC,const char[]);
PetscErrorCode PCAppendOptionsPrefix(PC,const char[]);
PetscErrorCode PCGetOptionsPrefix(PC,const char*[]);
PetscErrorCode PCSetFromOptions(PC);

PetscErrorCode PCSetUp(PC);
PetscErrorCode PCSetUpOnBlocks(PC);

PetscErrorCode PCApply(PC,Vec,Vec);
PetscErrorCode PCApplySymmetricLeft(PC,Vec,Vec);
PetscErrorCode PCApplySymmetricRight(PC,Vec,Vec);
PetscErrorCode PCApplyBAorAB(PC,PCSide,Vec,Vec,Vec);
PetscErrorCode PCApplyTranspose(PC,Vec,Vec);
PetscErrorCode PCHasApplyTranspose(PC,PetscTruth*);
PetscErrorCode PCApplyBAorABTranspose(PC,PCSide,Vec,Vec,Vec);
PetscErrorCode PCApplyRichardson(PC,Vec,Vec,Vec,PetscReal,PetscReal,PetscReal,PetscInt);
PetscErrorCode PCApplyRichardsonExists(PC,PetscTruth*);

/* ---------------------------------------------------------------- */

%wrapper %{
#define PCSetOperators(pc, A, P, matstr) \
        PCSetOperators(pc, A, (P==PETSC_NULL)?A:P, matstr)
%}

PetscErrorCode PCSetOperators(PC,Mat,Mat OBJ_OR_NONE,MatStructure);
PetscErrorCode PCGetOperators(PC,Mat* NEWREF,Mat* NEWREF,MatStructure*);

PetscErrorCode PCGetOperatorsSet(PC, PetscTruth *mat, PetscTruth *pmat);
PetscErrorCode PCGetFactoredMatrix(PC,Mat* NEWREF);
PetscErrorCode PCComputeExplicitOperator(PC, Mat* NEWOBJ);

PetscErrorCode PCDiagonalScale(PC,PetscTruth*);
PetscErrorCode PCDiagonalScaleLeft(PC,Vec,Vec);
PetscErrorCode PCDiagonalScaleRight(PC,Vec,Vec);
PetscErrorCode PCDiagonalScaleSet(PC,Vec);

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
