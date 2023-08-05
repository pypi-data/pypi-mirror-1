/* ---------------------------------------------------------------- */

%ignore KSPAddOptionsChecker;

%ignore KSPCGType;
%ignore KSPCGTypes;

/* ---------------------------------------------------------------- */

/* -- KSP events -- */

%ignore KSP_GMRESOrthogonalization;
%ignore KSP_SetUp;
%ignore KSP_Solve;

/* ---------------------------------------------------------------- */

/* -- KSP registering -- */

%ignore KSPInitializePackage;
%ignore KSPList;
%ignore KSPRegisterAll;
%ignore KSPRegisterDestroy;
%ignore KSPRegister;

/* ---------------------------------------------------------------- */

%ignore KSPDefaultBuildSolution;
%ignore KSPDefaultBuildResidual;

%ignore KSPSingularValueMonitor;
%ignore KSPDefaultMonitor;
%ignore KSPTrueMonitor;
%ignore KSPDefaultSMonitor;
%ignore KSPVecViewMonitor;

%ignore KSPGMRESKrylovMonitor;

%ignore KSPLGMonitor;
%ignore KSPLGMonitorCreate;
%ignore KSPLGMonitorDestroy;
%ignore KSPLGTrueMonitorCreate;
%ignore KSPLGTrueMonitor;
%ignore KSPLGTrueMonitorDestroy;


%ignore KSPRichardsonSetScale;
%ignore KSPChebychevSetEigenvalues;

%ignore KSPGMRESSetRestart;
%ignore KSPGMRESSetHapTol;
%ignore KSPGMRESSetPreAllocateVectors;
%ignore KSPGMRESSetOrthogonalization;
%ignore KSPGMRESModifiedGramSchmidtOrthogonalization;
%ignore KSPGMRESClassicalGramSchmidtOrthogonalization;
%ignore KSPGMRESSetCGSRefinementType;

%ignore KSPLGMRESSetAugDim;
%ignore KSPLGMRESSetConstant;

%ignore KSPFGMRESModifyPCNoChange;
%ignore KSPFGMRESModifyPCKSP;
%ignore KSPFGMRESSetModifyPC;

%ignore KSPQCGSetTrustRegionRadius;
%ignore KSPQCGGetQuadratic;
%ignore KSPQCGGetTrialStepNorm;

%ignore KSPBCGSLSetXRes;
%ignore KSPBCGSLSetPol;
%ignore KSPBCGSLSetEll;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
