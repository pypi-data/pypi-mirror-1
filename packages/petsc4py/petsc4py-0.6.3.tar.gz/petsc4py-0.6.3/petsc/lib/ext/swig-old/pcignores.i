/* ---------------------------------------------------------------- */

/* PC registering */

%ignore PCList;
%ignore PCRegisterAllCalled;
%ignore PCRegister;
%ignore PCInitializePackage;
%ignore PCRegisterDestroy;
%ignore PCRegisterAll;

/* ---------------------------------------------------------------- */

/* PC events */

%ignore PC_SetUp;
%ignore PC_SetUpOnBlocks;
%ignore PC_Apply;
%ignore PC_ApplyCoarse;
%ignore PC_ApplyMultiple;
%ignore PC_ApplySymmetricLeft;
%ignore PC_ApplySymmetricRight;
%ignore PC_ModifySubMatrices;

/* ---------------------------------------------------------------- */



/* ------------- ignore methods of particular preconditioners --------- */

%ignore PCJacobiSetUseRowMax(PC);
%ignore PCJacobiSetUseAbs(PC);
%ignore PCSORSetSymmetric(PC,MatSORType);
%ignore PCSORSetOmega(PC,PetscReal);
%ignore PCSORSetIterations(PC,PetscInt,PetscInt);

%ignore PCEisenstatSetOmega(PC,PetscReal);
%ignore PCEisenstatNoDiagonalScaling(PC);

%ignore PCBJacobiSetUseTrueLocal(PC);
%ignore PCBJacobiSetTotalBlocks(PC,PetscInt,const PetscInt[]);
%ignore PCBJacobiSetLocalBlocks(PC,PetscInt,const PetscInt[]);

%ignore PCKSPSetUseTrue(PC);

%ignore PCShellSetApply(PC,PetscErrorCode (*)(void*,Vec,Vec)); 
%ignore PCShellSetApplyBA(PC,PetscErrorCode (*)(void*,PCSide,Vec,Vec,Vec)); 
%ignore PCShellSetApplyTranspose(PC,PetscErrorCode (*)(void*,Vec,Vec));
%ignore PCShellSetSetUp(PC,PetscErrorCode (*)(void*));
%ignore PCShellSetApplyRichardson(PC,PetscErrorCode (*)(void*,Vec,Vec,Vec,PetscReal,PetscReal,PetscReal,PetscInt));
%ignore PCShellSetView(PC,PetscErrorCode (*)(void*,PetscViewer));
%ignore PCShellSetDestroy(PC,PetscErrorCode (*)(void*));
%ignore PCShellGetContext(PC,void**);
%ignore PCShellSetContext(PC,void*);
%ignore PCShellSetName(PC,const char[]);
%ignore PCShellGetName(PC,char*[]);

%ignore PCFactorSetZeroPivot(PC,PetscReal);
%ignore PCFactorSetShiftNonzero(PC,PetscReal); 
%ignore PCFactorSetShiftPd(PC,PetscTruth); 


%ignore PCFactorSetFill(PC,PetscReal);
%ignore PCFactorSetPivoting(PC,PetscReal);
%ignore PCFactorReorderForNonzeroDiagonal(PC,PetscReal);

%ignore PCFactorSetMatOrdering(PC,MatOrderingType);
%ignore PCFactorSetReuseOrdering(PC,PetscTruth);
%ignore PCFactorSetReuseFill(PC,PetscTruth);
%ignore PCFactorSetUseInPlace(PC);
%ignore PCFactorSetAllowDiagonalFill(PC);
%ignore PCFactorSetPivotInBlocks(PC,PetscTruth);

%ignore PCFactorSetLevels(PC,PetscInt);
%ignore PCFactorSetUseDropTolerance(PC,PetscReal,PetscReal,PetscInt);

%ignore PCASMSetLocalSubdomains(PC,PetscInt,IS[]);
%ignore PCASMSetTotalSubdomains(PC,PetscInt,IS[]);
%ignore PCASMSetOverlap(PC,PetscInt);

%ignore PCASMType;
%ignore PCASMTypes;

%ignore PCASMSetType(PC,PCASMType);
%ignore PCASMCreateSubdomains2D(PetscInt,PetscInt,PetscInt,PetscInt,PetscInt,PetscInt,PetscInt *,IS **);
%ignore PCASMSetUseInPlace(PC);
%ignore PCASMGetLocalSubdomains(PC,PetscInt*,IS*[]);
%ignore PCASMGetLocalSubmatrices(PC,PetscInt*,Mat*[]);

%ignore PCCompositeType;
%ignore PCCompositeTypes;

%ignore PCCompositeSetUseTrue(PC);
%ignore PCCompositeSetType(PC,PCCompositeType);
%ignore PCCompositeAddPC(PC,PCType);
%ignore PCCompositeGetPC(PC pc,PetscInt n,PC *);
%ignore PCCompositeSpecialSetAlpha(PC,PetscScalar);

%ignore PCRedundantSetScatter(PC,VecScatter,VecScatter);
%ignore PCRedundantGetOperators(PC,Mat*,Mat*);
%ignore PCRedundantGetPC(PC,PC*);

%ignore PCSPAISetEpsilon(PC,double);
%ignore PCSPAISetNBSteps(PC,PetscInt);
%ignore PCSPAISetMax(PC,PetscInt);
%ignore PCSPAISetMaxNew(PC,PetscInt);
%ignore PCSPAISetBlockSize(PC,PetscInt);
%ignore PCSPAISetCacheSize(PC,PetscInt);
%ignore PCSPAISetVerbose(PC,PetscInt);
%ignore PCSPAISetSp(PC,PetscInt);

%ignore PCHYPRESetType(PC,const char[]);
%ignore PCHYPREGetType(PC,const char*[]);
%ignore PCBJacobiGetLocalBlocks(PC,PetscInt*,const PetscInt*[]);
%ignore PCBJacobiGetTotalBlocks(PC,PetscInt*,const PetscInt*[]);

%ignore PCFieldSplitSetFields(PC,PetscInt,PetscInt*);
%ignore PCFieldSplitSetType(PC,PCCompositeType);

%ignore PCGalerkinSetRestriction(PC,Mat);
%ignore PCGalerkinSetInterpolation(PC,Mat);

%ignore PCSetCoordinates(PC,PetscInt,PetscReal*);
%ignore PCSASetVectors(PC,PetscInt,PetscReal *);

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
