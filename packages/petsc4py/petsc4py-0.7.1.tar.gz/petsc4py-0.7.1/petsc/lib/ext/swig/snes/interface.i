/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode SNESCreate(MPI_Comm,SNES* CREATE);
PetscErrorCode SNESDestroy(SNES);
PetscErrorCode SNESSetType(SNES,SNESType);
PetscErrorCode SNESGetType(SNES,SNESType*);
PetscErrorCode SNESView(SNES,PetscViewer);
PetscErrorCode SNESSetOptionsPrefix(SNES,const char[]);
PetscErrorCode SNESAppendOptionsPrefix(SNES,const char[]);
PetscErrorCode SNESGetOptionsPrefix(SNES,const char*[]);
PetscErrorCode SNESSetFromOptions(SNES);
PetscErrorCode SNESSetUp(SNES);

/* ---------------------------------------------------------------- */

PetscErrorCode SNESGetKSP(SNES, KSP* NEWREF);
PetscErrorCode SNESSetKSP(SNES, KSP);

PetscErrorCode SNESGetSolution(SNES, Vec* NEWREF);
PetscErrorCode SNESGetSolutionUpdate(SNES, Vec* NEWREF);

PetscErrorCode SNESSolve(SNES,Vec OPTIONAL,Vec OPTIONAL);

PetscErrorCode SNESSetRhs(SNES,Vec);
PetscErrorCode SNESGetRhs(SNES,Vec* NEWREF);

PetscErrorCode SNESTestLocalMin(SNES);
PetscErrorCode SNESSetSolution(SNES,Vec);

PetscErrorCode SNESComputeFunction(SNES,Vec,Vec);
PetscErrorCode SNESComputeJacobian(SNES,Vec,Mat* INOUT,Mat* INOUT,MatStructure*);

/* ---------------------------------------------------------------- */

PetscErrorCode SNESSetTolerances(SNES,PetscReal,PetscReal,PetscReal,PetscInt,PetscInt);
PetscErrorCode SNESGetTolerances(SNES,PetscReal*,PetscReal*,PetscReal*,PetscInt*,PetscInt*);
PetscErrorCode SNESGetIterationNumber(SNES,PetscInt*);
PetscErrorCode SNESGetFunctionNorm(SNES,PetscScalar*);
PetscErrorCode SNESGetNumberUnsuccessfulSteps(SNES,PetscInt*);
PetscErrorCode SNESSetMaximumUnsuccessfulSteps(SNES,PetscInt);
PetscErrorCode SNESGetMaximumUnsuccessfulSteps(SNES,PetscInt*);
PetscErrorCode SNESGetLinearSolveFailures(SNES,PetscInt*);
PetscErrorCode SNESSetMaxLinearSolveFailures(SNES,PetscInt);
PetscErrorCode SNESGetMaxLinearSolveFailures(SNES,PetscInt*);
PetscErrorCode SNESGetNumberLinearIterations(SNES,PetscInt*);

/* ---------------------------------------------------------------- */

%wrapper %{

#undef __FUNCT__  
#define __FUNCT__ "SNESUpdatePython"
static 
PetscErrorCode
SNESUpdatePython(SNES snes, PetscInt step)
{
  PyObject*      update = NULL;
  PyObject*      ret    = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  
  ierr = PetscObjectQueryPyCtx((PetscObject)snes, "__update__", &update);CHKERRQ(ierr);
  if (update == Py_None) PetscFunctionReturn(0);
  update  = PyCtx_Get(update);
  if (update == NULL) goto fail;

  ret = PyCtx_CALL_FUNC(update, "O&l",
			PySNES_Ref, snes, (long)step);
  if (ret == NULL) goto fail;

  Py_DECREF(ret);
  PetscFunctionReturn(0);

 fail:
  Py_XDECREF(ret);
  PetscFunctionReturn(1);
}


#undef __FUNCT__  
#define __FUNCT__ "SNESFunctionPython"
static 
PetscErrorCode 
SNESFunctionPython(SNES snes, Vec x, Vec f, void *ctx) {
  PyObject* function = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;
  
  function = PyCtx_Get((PyObject*)ctx);
  if (function == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(function, "O&O&O&",
			     PySNES_Ref, snes,
			     PyVec_Ref,  x,
			     PyVec_Ref,  f);
  if (retvalue == NULL) goto fail;
  Py_DECREF(retvalue);
  PetscFunctionReturn(0);
  
 fail:
  Py_XDECREF(retvalue);
  PetscFunctionReturn(1);
}


#undef __FUNCT__  
#define __FUNCT__ "SNESJacobianPython"
static 
PetscErrorCode 
SNESJacobianPython(SNES snes,
		 Vec x,
		 Mat* J, Mat* P, MatStructure* matstr,
		 void *ctx) {
  PyObject* jacobian = NULL;
  PyObject* objJ     = NULL;
  PyObject* objP     = NULL;
  MatStructure ms    = DIFFERENT_NONZERO_PATTERN;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;

  jacobian  = PyCtx_Get((PyObject*)ctx);
  if (jacobian == NULL) goto fail;
  objJ = PyMat_Ref(*J); if (objJ == NULL)  goto fail;
  objP = PyMat_Ref(*P); if (objP == NULL)  goto fail;
  retvalue = PyCtx_CALL_FUNC(jacobian, "O&O&OO",
			     PySNES_Ref, snes,
			     PyVec_Ref,  x,
			     objJ, objP);
  if (retvalue == NULL) goto fail;

  /* get MatStructure value */
  if (retvalue != Py_None) {
    if (PyInt_Check(retvalue)) {
      ms = (MatStructure) PyInt_AS_LONG(retvalue);
      if (ms < SAME_NONZERO_PATTERN || ms > SUBSET_NONZERO_PATTERN) {
	PyErr_SetString(PyExc_ValueError,
			"SNES Jacobian returned an invalid "
			"value for Mat.Structure"); goto fail;
      }
    } else {
      PyErr_SetString(PyExc_TypeError,
		      "SNES Jacobian must return None or a valid "
		      "integer value for Mat.Structure"); goto fail;
    }
  }

  *J      = PyMat_VAL(objJ);
  *P      = PyMat_VAL(objP);
  *matstr = ms;
  
  Py_DECREF(objJ);
  Py_DECREF(objP);
  Py_DECREF(retvalue);
  
  PetscFunctionReturn(0);

 fail:
  Py_XDECREF(objJ);
  Py_XDECREF(objP);
  Py_XDECREF(retvalue);
  PetscFunctionReturn(1);
} 


#undef __FUNCT__  
#define __FUNCT__ "SNESMonitorPython"
static 
PetscErrorCode 
SNESMonitorPython(SNES snes, PetscInt its, PetscReal fgnorm, void *ctx)
{
  PyObject* monitor  = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;

  monitor = PyCtx_Get((PyObject*)ctx);
  if (monitor == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(monitor, "O&ld",
			     PySNES_Ref, snes,
			     (long)its,(double)fgnorm);
  if (retvalue == NULL) goto fail;
  Py_DECREF(retvalue);

  PetscFunctionReturn(0);
  
 fail:
  Py_XDECREF(retvalue);
  PetscFunctionReturn(1);
}

#undef __FUNCT__  
#define __FUNCT__ "SNESMonitorPythonDestroy"
static PetscErrorCode
SNESMonitorPythonDestroy(void *ctx) {
  PetscFunctionBegin;
  if (ctx != NULL && PyCtx_Check((PyObject*)ctx)) {
    Py_DECREF((PyObject*)ctx);
  }
  PetscFunctionReturn(0);
}

%}

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
SNESSetUpdate,
(SNES snes, PyObject *update), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(update);
  if (ctx == NULL) SETERRQ(1,"invalid Update object");
  ierr = PetscObjectComposePyCtx((PetscObject)snes, "__update__", ctx); CHKERRQ(ierr);
  if (ctx != Py_None) {
    ierr = SNESSetUpdate(snes,SNESUpdatePython); CHKERRQ(ierr);
  } else {
    ierr = SNESSetUpdate(snes,NULL); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})


%apply Vec *NEWREF { Vec *r };
%apply PyObject **OUTPUT { PyObject **function };

PETSC_OVERRIDE(
PetscErrorCode,
SNESGetFunction,
(SNES snes, Vec *r, PyObject **function), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;

  ierr = SNESGetFunction(snes, r, NULL,
			 (void**)&ctx); CHKERRQ(ierr);
  if (PyCtx_Check(ctx)) {
    *function = PyCtx_Get(ctx);
    if (*function == NULL) goto fail;
  } else {
    *function = Py_None;
  }
  Py_INCREF(*function);

  PetscFunctionReturn(0);

 fail:
  PetscFunctionReturn(1);
})

%clear Vec *r, PyObject **function;

PETSC_OVERRIDE(
PetscErrorCode,
SNESSetFunction,
(SNES snes, Vec r, PyObject *function), {
  PyObject*      ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;

  ctx = PyCtx_New(function);
  if (ctx == NULL) SETERRQ(1,"invalid Function object");
  ierr = PetscObjectComposePyCtx((PetscObject)snes, "__function__", ctx); CHKERRQ(ierr);
  ierr = PetscObjectCompose((PetscObject)snes, "__fun_vec__", (PetscObject)r); CHKERRQ(ierr);
  ierr = SNESSetFunction(snes, r, SNESFunctionPython, (void*)ctx); CHKERRQ(ierr);

  PetscFunctionReturn(0);
})


%apply Mat* NEWREF { Mat *J, Mat *P };
%apply PyObject **OUTPUT { PyObject **jacobian };

PETSC_OVERRIDE(
PetscErrorCode,
SNESGetJacobian,
(SNES snes, Mat *J, Mat *P, PyObject **jacobian), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESGetJacobian(snes, J, P, NULL,
			 (void**)&ctx); CHKERRQ(ierr);
  if (PyCtx_Check(ctx)) {
    *jacobian = PyCtx_Get(ctx);
    if (*jacobian == NULL) goto fail;
  } else {
    *jacobian = Py_None;
  }
  Py_INCREF(*jacobian);

  PetscFunctionReturn(0);

 fail:
  PetscFunctionReturn(1);
})

%clear Mat *J, Mat *P, PyObject **jacobian;


%apply Mat OPTIONAL { Mat A, Mat P };

PETSC_OVERRIDE(
PetscErrorCode,
SNESSetJacobian,
(SNES snes, Mat A, Mat P, PyObject *jacobian), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(jacobian);
  if (ctx == NULL) SETERRQ(1,"invalid Jacobian object");
  ierr = PetscObjectComposePyCtx((PetscObject)snes, "__jacobian__", ctx); CHKERRQ(ierr);
  ierr = SNESSetJacobian(snes, A, (P==PETSC_NULL)? A : P,
			 SNESJacobianPython, (void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear Mat A, Mat P;

/* ---------------------------------------------------------------- */

%apply PyObject **OUTPUT { PyObject **appctx };

PETSC_OVERRIDE(
PetscErrorCode,
SNESGetApplicationContext,
(SNES snes, PyObject **appctx), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESGetApplicationContext(snes, (void**)&ctx); CHKERRQ(ierr);
  if (PyCtx_Check(ctx)) {
    *appctx = PyCtx_Get(ctx);
    if (*appctx == NULL) goto fail;
  } else {
    *appctx = Py_None;
  }
  Py_INCREF(*appctx);
  PetscFunctionReturn(0);
 fail:
  PetscFunctionReturn(1);
})

%clear PyObject **appctx;

PETSC_OVERRIDE(
PetscErrorCode,
SNESSetApplicationContext,
(SNES snes, PyObject *appctx), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(appctx);
  if (ctx == NULL) SETERRQ(1,"invalid ApplicationContext object");
  ierr = PetscObjectComposePyCtx((PetscObject)snes, "__appctx__", ctx); CHKERRQ(ierr);
  ierr = SNESSetApplicationContext(snes,(void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})


/* ---------------------------------------------------------------- */

PetscErrorCode SNESMonitorCancel(SNES snes);

PETSC_OVERRIDE(
PetscErrorCode,
SNESMonitorSet, 
(SNES snes, PyObject *monitor), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (monitor == Py_None) SETERRQ(1,"SNES Monitor cannot be None");
  ctx = PyCtx_New(monitor);
  if (ctx == NULL) SETERRQ(1,"invalid SNES Monitor object");
  ierr = SNESMonitorSet(snes, SNESMonitorPython, (void*)ctx,
			SNESMonitorPythonDestroy); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})



PETSC_OVERRIDE(
PetscErrorCode,
SNESMonitorDefault,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESMonitorDefault(snes, its, fgnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESMonitorSolution,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESMonitorSolution(snes, its, fgnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESMonitorResidual,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESMonitorResidual(snes, its, fgnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESMonitorSolutionUpdate,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESMonitorSolutionUpdate(snes, its, fgnorm, NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

PetscErrorCode SNESGetConvergedReason(SNES,SNESConvergedReason*);

%wrapper %{
#undef __FUNCT__
#define __FUNCT__ "SNESConvergedPython"
static PetscErrorCode 
SNESConvergedPython(SNES snes, PetscInt its,
			PetscReal xnorm, PetscReal gnorm, PetscReal fnorm,
			SNESConvergedReason *reason, void *ctx)
{
  PyObject* convtest = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;

  convtest = PyCtx_Get((PyObject*)ctx);
  if (convtest == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(convtest, "O&iddd",
			     PySNES_Ref, snes, (int)its,
			     (double)xnorm, (double)gnorm, (double)fnorm);
  if (retvalue == NULL) goto fail;

  /* get SNESConvergedReason value */
  if (retvalue == Py_None)
    *reason = SNES_CONVERGED_ITERATING;
  else if (PyInt_Check(retvalue)) {
    *reason = (SNESConvergedReason) PyInt_AS_LONG(retvalue);
    if (*reason < SNES_DIVERGED_LOCAL_MIN || 
	*reason > SNES_CONVERGED_TR_DELTA) {
      PyErr_SetString(PyExc_ValueError,
		      "SNES Convergence Test returned an invalid "
		      "value for SNES.ConvergedReason"); goto fail;
    }
  } else {
    PyErr_SetString(PyExc_TypeError,
		    "SNES Convergence Test must return None or a valid "
		    "integer value for SNES.ConvergedReason"); goto fail;
  }
  Py_DECREF(retvalue);

  PetscFunctionReturn(0);
  
 fail:
  Py_XDECREF(retvalue);
  PetscFunctionReturn(1);
} 
%}

PETSC_OVERRIDE(
PetscErrorCode,
SNESSetConvergenceTest,
(SNES snes, PyObject *convtest), {
  PyObject*      ctx  = NULL;
  PetscTruth     flag = PETSC_FALSE;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (convtest == NULL || convtest == Py_None) {
    ierr = PetscObjectCompose((PetscObject)snes, "__convtest__", PETSC_NULL); CHKERRQ(ierr);
    /* line search */
    ierr = PetscTypeCompare((PetscObject)snes, SNESLS, &flag);CHKERRQ(ierr);
    if (flag) {
      ierr = SNESSetConvergenceTest(snes,SNESConverged_LS,PETSC_NULL);CHKERRQ(ierr);
      PetscFunctionReturn(0);
    }
    /* trust region */
    ierr = PetscTypeCompare((PetscObject)snes, SNESTR, &flag);CHKERRQ(ierr);
    if (flag) {
      ierr = SNESSetConvergenceTest(snes,SNESConverged_TR,PETSC_NULL);CHKERRQ(ierr);
      PetscFunctionReturn(0);
    }
    /* default to line search */
    ierr = SNESSetConvergenceTest(snes,SNESConverged_LS,PETSC_NULL);CHKERRQ(ierr);
    PetscFunctionReturn(0);
  } else {
    /* user-provided routine */
    if (!PyCallable_Check(convtest)) SETERRQ(1,"SNES Convergence Test is not callable");
    ctx = PyCtx_New(convtest); if (ctx == NULL) SETERRQ(1,"invalid SNES Convergence Test object");
    ierr = PetscObjectComposePyCtx((PetscObject)snes, "__convtest__", ctx); CHKERRQ(ierr);
    ierr = SNESSetConvergenceTest(snes, SNESConvergedPython, (void*)ctx); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESDefaultConvergenceTest,
(SNES snes,PetscInt its, PetscReal xnorm,PetscReal gnorm,PetscReal fnorm,
 SNESConvergedReason *reason), {
  PetscTruth flag = PETSC_FALSE;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  /* line search */
  ierr = PetscTypeCompare((PetscObject)snes, SNESLS, &flag);CHKERRQ(ierr);
  if (flag) {
    ierr = SNESConverged_LS(snes, its, xnorm, gnorm, fnorm, 
			    reason, PETSC_NULL); CHKERRQ(ierr);
    PetscFunctionReturn(0);
  }
  /* trust region */
  ierr = PetscTypeCompare((PetscObject)snes, SNESTR, &flag);CHKERRQ(ierr);
  if (flag) {
    ierr = SNESConverged_TR(snes, its, xnorm, gnorm, fnorm, 
			    reason, PETSC_NULL); CHKERRQ(ierr);
    PetscFunctionReturn(0);
  }
  /* default */
  ierr = SNESConverged_LS(snes, its, xnorm, gnorm, fnorm,
			  reason, PETSC_NULL); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

ARRAY_1D_NEW(PetscInt* na, PetscReal* a[], PyPetsc_REAL)
ARRAY_1D_NEW(PetscInt* ni, PetscInt*  i[], PyPetsc_INT)

PETSC_OVERRIDE(
PetscErrorCode,
SNESGetConvergenceHistory,
(SNES snes,PetscInt* na,PetscReal* a[],PetscInt* ni,PetscInt* i[]), {
  PetscErrorCode ierr;
  PetscInt       nn;
  PetscReal      *aa;
  PetscInt       *ii;
  PetscFunctionBegin;
  ierr = SNESGetConvergenceHistory(snes,&aa,&ii,&nn); CHKERRQ(ierr);
  if (aa == PETSC_NULL || ii == PETSC_NULL) nn = 0;
  *na = nn; *a  = aa;
  *ni = nn; *i  = ii;
  PetscFunctionReturn(0);
})

%clear (PetscInt* na,PetscReal* a[]);
%clear (PetscInt* ni,PetscInt*  i[]);

%wrapper %{

typedef struct SNESConvHist {
  PetscReal *a;
  PetscInt  *its;
} SNESConvHist;

static
PetscErrorCode SNESConvHistoryFree(void *h)
{
  PetscErrorCode ierr;
  SNESConvHist   *ch = (SNESConvHist*)h;
  PetscFunctionBegin;
  ierr = PetscFree(ch->a);CHKERRQ(ierr);
  ierr = PetscFree(ch->its);CHKERRQ(ierr);
  ierr = PetscFree(ch);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

static
PetscErrorCode SNESAllocConvHistory(SNES snes, PetscInt n, PetscTruth reset)
{
  PetscErrorCode ierr;
  SNESConvHist   *ch;
  MPI_Comm       comm;
  PetscContainer container;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(snes,SNES_COOKIE,1);
  /* */
  if (n == PETSC_DECIDE || n == PETSC_DEFAULT) {
    ierr = SNESGetTolerances(snes,PETSC_NULL,PETSC_NULL,PETSC_NULL,&n,PETSC_NULL);CHKERRQ(ierr);
    n = PetscMax(n,0); n = PetscMin(n,10000);
  } else if (n <= 0) n = 0;

  /* clear convergence history */
  if (n == 0) {
    ierr = PetscObjectCompose((PetscObject)snes,"__conv_hist_alloc",PETSC_NULL);CHKERRQ(ierr);
    ierr = SNESSetConvergenceHistory(snes,PETSC_NULL,PETSC_NULL,0,PETSC_TRUE); CHKERRQ(ierr);
    PetscFunctionReturn(0);
  }
  /* allocate array to hold residual history */
  ierr = PetscMalloc(sizeof(SNESConvHist),&ch);CHKERRQ(ierr);
  ierr = PetscMalloc(n*sizeof(PetscReal),&ch->a);CHKERRQ(ierr);
  ierr = PetscMalloc(n*sizeof(PetscReal),&ch->its);CHKERRQ(ierr);
  /* cache array in a containter */
  ierr = PetscObjectGetComm((PetscObject)snes,&comm);CHKERRQ(ierr);
  ierr = PetscContainerCreate(comm,&container);CHKERRQ(ierr);
  ierr = PetscContainerSetUserDestroy(container,SNESConvHistoryFree);CHKERRQ(ierr);
  ierr = PetscContainerSetPointer(container,(void*)ch);CHKERRQ(ierr);
  ierr = PetscObjectCompose((PetscObject)snes,"__conv_hist_alloc",(PetscObject)container);CHKERRQ(ierr);
  ierr = PetscContainerDestroy(container);CHKERRQ(ierr);
  /* set the allocated array */
  ierr = SNESSetConvergenceHistory(snes,ch->a,ch->its,n,reset); CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
%}

PetscErrorCode SNESAllocConvHistory(SNES,PetscInt,PetscTruth);

/* ---------------------------------------------------------------- */

%header %{
#include "include/private/snesimpl.h"
%}

%wrapper %{

#undef __FUNCT__  
#define __FUNCT__ "SNESSetUseEW"
static PetscErrorCode
SNESGetUseEW(SNES snes, PetscTruth *flag)
{
  PetscFunctionBegin;
  PetscValidHeaderSpecific(snes,SNES_COOKIE,1);
  PetscValidIntPointer(flag,2);
  *flag = snes->ksp_ewconv;
  PetscFunctionReturn(0);
}

#undef __FUNCT__  
#define __FUNCT__ "SNESSetUseEW"
static PetscErrorCode
SNESSetUseEW(SNES snes, PetscTruth flag)
{
  PetscFunctionBegin;
  PetscValidHeaderSpecific(snes,SNES_COOKIE,1);
  snes->ksp_ewconv = flag;
  PetscFunctionReturn(0);
}

#undef __FUNCT__  
#define __FUNCT__ "SNESSetParametersEW"
static PetscErrorCode
SNESSetParametersEW(SNES snes,
		    PetscInt  version,
		    PetscReal rtol_0,
		    PetscReal rtol_max,
		    PetscReal gamma2,
		    PetscReal alpha,
		    PetscReal alpha2,
		    PetscReal threshold)
{
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(snes,SNES_COOKIE,1);
  ierr = SNES_KSP_SetParametersEW(snes,version,rtol_0,rtol_max,
				  gamma2,alpha,alpha2,threshold);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

%}

PetscErrorCode SNESGetUseEW(SNES,PetscTruth*);
PetscErrorCode SNESSetUseEW(SNES,PetscTruth);
PetscErrorCode SNESSetParametersEW(SNES snes,
				   PetscInt  version,
				   PetscReal rtol_0,
				   PetscReal rtol_max,
				   PetscReal gamma2,
				   PetscReal alpha,
				   PetscReal alpha2,
				   PetscReal threshold);

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
