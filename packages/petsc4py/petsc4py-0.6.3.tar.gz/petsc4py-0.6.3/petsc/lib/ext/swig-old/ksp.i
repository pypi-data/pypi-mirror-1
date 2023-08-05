/* $Id$ */

%include context.i

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode
KSPCreate(MPI_Comm, KSP* CREATE);

/* ---------------------------------------------------------------- */

%wrapper %{
#define KSPSetOperators(ksp, A, P, matstr) \
        KSPSetOperators(ksp, A, (P==PETSC_NULL)?A:P, matstr)
%}

PetscErrorCode
KSPGetOperators(KSP, Mat* NEWREF, Mat* NEWREF, MatStructure*);

PetscErrorCode
KSPSetOperators(KSP, Mat, Mat OBJ_OR_NONE, MatStructure);

PetscErrorCode
KSPGetOperatorsSet(KSP, PetscTruth *mat, PetscTruth *pmat);

PetscErrorCode
KSPGetPC(KSP, PC* NEWREF);

PetscErrorCode
KSPGetNullSpace(KSP, MatNullSpace* NEWREF);

PetscErrorCode
KSPGetRhs(KSP, Vec* NEWREF);

PetscErrorCode
KSPGetSolution(KSP, Vec* NEWREF);

/* ---------------------------------------------------------------- */

PetscErrorCode
KSPComputeExplicitOperator(KSP, Mat* NEWOBJ);

%wrapper %{
#define KSPBuildSolution(ksp, sol) \
        KSPBuildSolution(ksp,sol,PETSC_NULL)
%}
PetscErrorCode
KSPBuildSolution(KSP ksp, Vec sol);
%ignore KSPBuildSolution;

PETSC_OVERRIDE(
PetscErrorCode,
KSPBuildResidual,(KSP ksp, Vec res), {
  Vec            V;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPBuildResidual(ksp,PETSC_NULL,res,&V); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

ARRAY_1D_NEW(PetscInt* nrh, PetscReal* rh[],
	     PyPetsc_REAL)

PETSC_OVERRIDE(
PetscErrorCode,
KSPGetResidualHistory,
(KSP ksp,PetscInt* nrh,PetscReal* rh[]), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPGetResidualHistory(ksp,rh,nrh); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt* nrh, PetscReal* rh[]);


ARRAY_RAW(PetscReal rh[],
	  ARRAY_INPUT, PyPetsc_REAL)

PetscErrorCode 
KSPSetResidualHistory(KSP,
		      PetscReal rh[],PetscInt nrh,
		      PetscTruth reset);

%clear PetscReal rh[];

/* ---------------------------------------------------------------- */

ARRAY_PAIR(PetscInt n, PetscReal r[], PetscReal c[],
	   ARRAY_OUTPUT, PyPetsc_REAL,
	   ARRAY_OUTPUT, PyPetsc_REAL)
ARRAY_PAIR_CHECK_SIZE(PetscInt n, PetscReal r[], PetscReal c[])

PetscErrorCode
KSPComputeEigenvalues(KSP ksp,
		      PetscInt n,PetscReal r[],PetscReal c[],
		      PetscInt *neig);
PetscErrorCode
KSPComputeEigenvaluesExplicitly(KSP ksp,
				PetscInt n,PetscReal r[],PetscReal c[]);

%ignore KSPComputeEigenvalues;
%ignore KSPComputeEigenvaluesExplicitly;

%clear (PetscInt n, PetscReal r[], PetscReal c[]);


/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "PyKSP_Monitor"
static 
PetscErrorCode 
_PyKSP_Monitor(KSP ksp, PetscInt its, PetscReal rnorm, void *ctx)
{
  PyObject* monitor  = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;

  monitor = PyCtx_Get((PyObject*)ctx);
  if (monitor == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(monitor, "O&ld",
			     PyKSP_Ref, ksp,
			     (long)its, (double)rnorm);
  if (retvalue == NULL) goto fail;
  Py_DECREF(retvalue);
  
  PetscFunctionReturn(0);
  
 fail:
  Py_XDECREF(retvalue);
  return 1;
}

#undef __FUNCT__  
#define __FUNCT__ "PyKSP_DestroyMonitor"
static
PetscErrorCode
_PyKSP_MonitorDestroy(void *ctx) 
{
  PetscFunctionBegin;
  if (ctx != NULL && PyCtx_Check((PyObject*)ctx)) {
    Py_DECREF((PyObject*)ctx);
  }
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "PyKSP_ConvergenceTest"
static 
PetscErrorCode 
_PyKSP_ConvergenceTest(KSP ksp,
		       PetscInt its, PetscReal rnorm,
		       KSPConvergedReason* reason, void* ctx) 
{
  PyObject* convtest = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;

  convtest = PyCtx_Get((PyObject*)ctx);
  if (convtest == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(convtest, "O&ll",
			     PyKSP_Ref, ksp,
			     (long)its, (double)rnorm);
  if (retvalue == NULL) goto fail;

  /* get KSPConvergedReason value */
  if (retvalue == Py_None)
    *reason = KSP_CONVERGED_ITERATING;
  else if (PyInt_Check(retvalue)) {
    *reason = (KSPConvergedReason) PyInt_AS_LONG(retvalue);
    if (*reason < KSP_DIVERGED_INDEFINITE_MAT ||
	*reason > KSP_CONVERGED_STEP_LENGTH) {
      PyErr_SetString(PyExc_ValueError,
		      "KSP Convergence Test returned "
		      "an invalid value for KSP.ConvergedReason");
    }
  } else {
    PyErr_SetString(PyExc_TypeError,
		    "SNES Convergence Test must return None or a valid "
		    "integer value for KSP.ConvergedReason"); goto fail;
  }
  Py_DECREF(retvalue);
  
  PetscFunctionReturn(0);

 fail:
  Py_XDECREF(retvalue);
  return 1;
} 

%}

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
KSPSetMonitor, 
(KSP ksp, PyObject *monitor), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (monitor == Py_None) SETERRQ(1,"KSP Monitor cannot be None");
  ctx = PyCtx_New(monitor);
  if (ctx == NULL) SETERRQ(1,"invalid KSP Monitor object");
  ierr = KSPSetMonitor(ksp, _PyKSP_Monitor, (void*)ctx,
		       _PyKSP_MonitorDestroy); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPDefaultMonitor,
(KSP ksp,PetscInt n,PetscReal rnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPDefaultMonitor(ksp, n, rnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPTrueMonitor,
(KSP ksp,PetscInt n,PetscReal rnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPTrueMonitor(ksp, n, rnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPVecViewMonitor,
(KSP ksp,PetscInt n,PetscReal rnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPVecViewMonitor(ksp, n, rnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPSetNormType, 
(KSP ksp, KSPNormType normtype), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (normtype == KSP_NO_NORM) {
    ierr = PetscObjectComposePyCtx((PetscObject)ksp, "__convtest__", NULL);
    ierr = KSPSetConvergenceTest(ksp, KSPSkipConverged, 0);CHKERRQ(ierr);
  }
  ierr = KSPSetNormType(ksp, normtype);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPDefaultConverged,
(KSP ksp,PetscInt n,PetscReal rnorm,KSPConvergedReason *reason), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPDefaultConverged(ksp, n, rnorm, reason, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPSkipConverged,
(KSP ksp,PetscInt n,PetscReal rnorm,KSPConvergedReason *reason), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPSkipConverged(ksp, n, rnorm, reason, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%ignore KSPDefaultConverged;
%ignore KSPSkipConverged;

PETSC_OVERRIDE(
PetscErrorCode,
KSPSetConvergenceTest, 
(KSP ksp, PyObject *convtest), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(convtest);
  if (ctx == NULL) SETERRQ(1,"invalid KSP Convergence Test object");
  ierr = PetscObjectComposePyCtx((PetscObject)ksp, "__convtest__", ctx); CHKERRQ(ierr);
  if (ctx == Py_None) {
    ierr = KSPSetConvergenceTest(ksp, KSPDefaultConverged, NULL);CHKERRQ(ierr);
  } else {
    ierr = KSPSetConvergenceTest(ksp, _PyKSP_ConvergenceTest, (void*)ctx);CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore KSPAddOptionsChecker;

%ignore KSPCGType;
%ignore KSPCGTypes;

%ignore KSP_GMRESOrthogonalization;
%ignore KSP_SetUp;
%ignore KSP_Solve;
%ignore KSPList;

%ignore KSPInitializePackage;
%ignore KSPRegisterAll;
%ignore KSPRegisterDestroy;
%ignore KSPRegister;

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
