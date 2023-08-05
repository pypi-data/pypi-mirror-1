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

PetscErrorCode PCSetOperators(PC,Mat,Mat OPTIONAL,MatStructure);
PetscErrorCode PCGetOperators(PC,Mat* NEWREF,Mat* NEWREF,MatStructure*);

PetscErrorCode PCGetOperatorsSet(PC, PetscTruth *mat, PetscTruth *pmat);
PetscErrorCode PCComputeExplicitOperator(PC, Mat* NEWOBJ);

PetscErrorCode PCDiagonalScale(PC,PetscTruth*);
PetscErrorCode PCDiagonalScaleLeft(PC,Vec,Vec);
PetscErrorCode PCDiagonalScaleRight(PC,Vec,Vec);
PetscErrorCode PCDiagonalScaleSet(PC,Vec);

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
