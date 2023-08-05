/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode KSPCreate(MPI_Comm, KSP* CREATE);
PetscErrorCode KSPDestroy(KSP);
PetscErrorCode KSPView(KSP,PetscViewer);

PetscErrorCode KSPSetType(KSP,KSPType);
PetscErrorCode KSPGetType(KSP,KSPType*);

PetscErrorCode KSPSetOptionsPrefix(KSP,const char[]);
PetscErrorCode KSPAppendOptionsPrefix(KSP,const char[]);
PetscErrorCode KSPGetOptionsPrefix(KSP,const char*[]);
PetscErrorCode KSPSetFromOptions(KSP);

PetscErrorCode KSPSetPreconditionerSide(KSP,PCSide);
PetscErrorCode KSPGetPreconditionerSide(KSP,PCSide*);
PetscErrorCode KSPGetTolerances(KSP,PetscReal*,PetscReal*,PetscReal*,PetscInt*);
PetscErrorCode KSPSetTolerances(KSP,PetscReal,PetscReal,PetscReal,PetscInt);
PetscErrorCode KSPSetInitialGuessNonzero(KSP,PetscTruth);
PetscErrorCode KSPGetInitialGuessNonzero(KSP,PetscTruth*);
PetscErrorCode KSPSetInitialGuessKnoll(KSP,PetscTruth);
PetscErrorCode KSPGetInitialGuessKnoll(KSP,PetscTruth*);
PetscErrorCode KSPGetComputeEigenvalues(KSP,PetscTruth*);
PetscErrorCode KSPSetComputeEigenvalues(KSP,PetscTruth);
PetscErrorCode KSPGetComputeSingularValues(KSP,PetscTruth*);
PetscErrorCode KSPSetComputeSingularValues(KSP,PetscTruth);

PetscErrorCode KSPSetUp(KSP);
PetscErrorCode KSPSetUpOnBlocks(KSP);
PetscErrorCode KSPSolve(KSP,Vec,Vec);
PetscErrorCode KSPSolveTranspose(KSP,Vec,Vec);

/* ---------------------------------------------------------------- */

PetscErrorCode KSPGetRhs(KSP,Vec* NEWREF);
PetscErrorCode KSPGetSolution(KSP,Vec* NEWREF);
PetscErrorCode KSPGetResidualNorm(KSP,PetscReal*);
PetscErrorCode KSPGetIterationNumber(KSP,PetscInt*);
PetscErrorCode KSPSetNullSpace(KSP,MatNullSpace);
PetscErrorCode KSPGetNullSpace(KSP,MatNullSpace* NEWREF);

PetscErrorCode KSPSetPC(KSP,PC);
PetscErrorCode KSPGetPC(KSP,PC* NEWREF);

%wrapper %{
#define KSPSetOperators(ksp, A, P, matstr) \
        KSPSetOperators(ksp, A, (P==PETSC_NULL)?A:P, matstr)
%}


PetscErrorCode KSPGetOperators(KSP,Mat* NEWREF,Mat* NEWREF,MatStructure*);
PetscErrorCode KSPSetOperators(KSP,Mat,Mat OBJ_OR_NONE,MatStructure);
PetscErrorCode KSPGetOperatorsSet(KSP,PetscTruth*, PetscTruth*);

PetscErrorCode KSPSetDiagonalScale(KSP,PetscTruth);
PetscErrorCode KSPGetDiagonalScale(KSP,PetscTruth*);
PetscErrorCode KSPSetDiagonalScaleFix(KSP,PetscTruth);
PetscErrorCode KSPGetDiagonalScaleFix(KSP,PetscTruth*);

/* ---------------------------------------------------------------- */

PetscErrorCode KSPComputeExplicitOperator(KSP, Mat* NEWOBJ);

PETSC_OVERRIDE(
PetscErrorCode,
KSPBuildSolution,(KSP ksp, Vec sol), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPBuildSolution(ksp,sol,NULL); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

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

ARRAY_1D_NEW(PetscInt* nr, PetscReal* r[],
	     PyPetsc_REAL)

PETSC_OVERRIDE(
PetscErrorCode,
KSPGetResidualHistory,
(KSP ksp,PetscInt* nr,PetscReal* r[]), {
  PetscErrorCode ierr;
  PetscInt       nn;
  PetscReal      *rr;
  PetscFunctionBegin;
  ierr = KSPGetResidualHistory(ksp,&rr,&nn); CHKERRQ(ierr);
  if (rr == PETSC_NULL) nn = 0;
  *nr = nn; *r = rr;
  PetscFunctionReturn(0);
})

%clear (PetscInt* nr, PetscReal* r[]);

%wrapper %{
static
PetscErrorCode KSPResHistFree(void *rh)
{
  PetscErrorCode   ierr;
  PetscFunctionBegin;
  ierr = PetscFree(rh);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

static
PetscErrorCode KSPLogResidualHistory(KSP ksp, PetscInt n, PetscTruth reset)
{
  PetscErrorCode       ierr;
  PetscReal            *rh;
  MPI_Comm             comm;
  PetscObjectContainer container;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(ksp,KSP_COOKIE,1);
  /* */
  if (n == PETSC_DECIDE || n == PETSC_DEFAULT) {
    ierr = KSPGetTolerances(ksp,PETSC_NULL,PETSC_NULL,PETSC_NULL,&n);CHKERRQ(ierr);
    n = PetscMax(n,0); n = PetscMin(n,10000);
  } else if  (n <= 0) n = 0;
  /* clear convergence history */
  if (n == 0) {
    static PetscReal dummy[1] = { 0 };
    ierr = PetscObjectCompose((PetscObject)ksp,"__reshist_data",PETSC_NULL);CHKERRQ(ierr);
    ierr = KSPSetResidualHistory(ksp,dummy,0,PETSC_TRUE); CHKERRQ(ierr);
    PetscFunctionReturn(0);
  }
  /* allocate array to hold residual history */
  ierr = PetscMalloc(n*sizeof(PetscReal),&rh);CHKERRQ(ierr);
  /* cache array in a containter */
  ierr = PetscObjectGetComm((PetscObject)ksp,&comm);CHKERRQ(ierr);
  ierr = PetscObjectContainerCreate(comm,&container);CHKERRQ(ierr);
  ierr = PetscObjectContainerSetUserDestroy(container,KSPResHistFree);CHKERRQ(ierr);
  ierr = PetscObjectContainerSetPointer(container,(void*)rh);CHKERRQ(ierr);
  ierr = PetscObjectCompose((PetscObject)ksp,"__reshist_data",(PetscObject)container);CHKERRQ(ierr);
  ierr = PetscObjectContainerDestroy(container);CHKERRQ(ierr);
  /* set the allocated array */
  ierr = KSPSetResidualHistory(ksp,rh,n,reset); CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
%}

PetscErrorCode KSPLogResidualHistory(KSP,PetscInt,PetscTruth);

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


%clear (PetscInt n, PetscReal r[], PetscReal c[]);

PetscErrorCode KSPComputeExtremeSingularValues(KSP,PetscReal*,PetscReal*);

/* ---------------------------------------------------------------- */

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

/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "KSPMonitorPython"
static 
PetscErrorCode 
KSPMonitorPython(KSP ksp, PetscInt its, PetscReal rnorm, void *ctx)
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
#define __FUNCT__ "KSPMonitorPythonDestroy"
static
PetscErrorCode
KSPMonitorPythonDestroy(void *ctx) 
{
  PetscFunctionBegin;
  if (ctx != NULL && PyCtx_Check((PyObject*)ctx)) {
    Py_DECREF((PyObject*)ctx);
  }
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "KSPConvergedPython"
static 
PetscErrorCode 
KSPConvergedPython(KSP ksp,
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

PetscErrorCode KSPMonitorCancel(KSP ksp);

PETSC_OVERRIDE(
PetscErrorCode,
KSPMonitorSet, 
(KSP ksp, PyObject *monitor), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (monitor == Py_None) SETERRQ(1,"KSP Monitor cannot be None");
  ctx = PyCtx_New(monitor);
  if (ctx == NULL) SETERRQ(1,"invalid KSP Monitor object");
  ierr = KSPMonitorSet(ksp, KSPMonitorPython, (void*)ctx,
		       KSPMonitorPythonDestroy); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPMonitorDefault,
(KSP ksp,PetscInt n,PetscReal rnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPMonitorDefault(ksp, n, rnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPMonitorTrueResidualNorm,
(KSP ksp,PetscInt n,PetscReal rnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPMonitorTrueResidualNorm(ksp, n, rnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
KSPMonitorSolution,
(KSP ksp,PetscInt n,PetscReal rnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPMonitorSolution(ksp, n, rnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

PetscErrorCode KSPGetConvergedReason(KSP,KSPConvergedReason*);

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
    ierr = KSPSetConvergenceTest(ksp, KSPConvergedPython, (void*)ctx);CHKERRQ(ierr);
  }
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

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
