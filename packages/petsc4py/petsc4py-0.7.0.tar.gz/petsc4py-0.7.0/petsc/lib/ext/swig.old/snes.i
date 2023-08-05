/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode 
SNESCreate(MPI_Comm, SNES* CREATE);

/* ---------------------------------------------------------------- */

PetscErrorCode
SNESGetKSP(SNES, KSP* NEWREF);

PetscErrorCode
SNESSetKSP(SNES, KSP);

PetscErrorCode
SNESGetRhs(SNES, Vec* NEWREF);

PetscErrorCode
SNESGetSolution(SNES, Vec* NEWREF);

PetscErrorCode
SNESGetSolutionUpdate(SNES, Vec* NEWREF);

PetscErrorCode 
SNESComputeJacobian(SNES, Vec x,
		    Mat* INOUT, Mat* INOUT, MatStructure*);

PetscErrorCode 
SNESSetSolution(SNES, Vec);

PetscErrorCode
SNESSolve(SNES, Vec OBJ_OR_NONE, Vec OBJ_OR_NONE);


/* ---------------------------------------------------------------- */

%include context.i

%wrapper %{

#undef __FUNCT__  
#define __FUNCT__ "PySNES_Update"
static 
PetscErrorCode
_PySNES_Update(SNES snes, PetscInt step)
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
#define __FUNCT__ "PySNES_Function"
static 
PetscErrorCode 
_PySNES_Function(SNES snes, Vec x, Vec f, void *ctx) {
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
#define __FUNCT__ "PySNES_Jacobian"
static 
PetscErrorCode 
_PySNES_Jacobian(SNES snes,
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
#define __FUNCT__ "PySNES_Monitor"
static 
PetscErrorCode 
_PySNES_Monitor(SNES snes, PetscInt its, PetscReal fgnorm, void *ctx)
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
#define __FUNCT__ "PySNES_MonitorDestroy"
static PetscErrorCode
_PySNES_MonitorDestroy(void *ctx) {
  PetscFunctionBegin;
  if (ctx != NULL && PyCtx_Check((PyObject*)ctx)) {
    Py_DECREF((PyObject*)ctx);
  }
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "PySNES_ConvergenceTest"
static PetscErrorCode 
_PySNES_ConvergenceTest(SNES snes, PetscInt its,
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
    ierr = SNESSetUpdate(snes,_PySNES_Update); CHKERRQ(ierr);
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
  ierr = SNESSetFunction(snes, r,_PySNES_Function, (void*)ctx); CHKERRQ(ierr);

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


%apply Mat OBJ_OR_NONE { Mat A, Mat P };

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
			 _PySNES_Jacobian, (void*)ctx); CHKERRQ(ierr);
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

PETSC_OVERRIDE(
PetscErrorCode,
SNESSetMonitor, 
(SNES snes, PyObject *monitor), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (monitor == Py_None) SETERRQ(1,"SNES Monitor cannot be None");
  ctx = PyCtx_New(monitor);
  if (ctx == NULL) SETERRQ(1,"invalid SNES Monitor object");
  ierr = SNESSetMonitor(snes, _PySNES_Monitor, (void*)ctx,
			_PySNES_MonitorDestroy); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESDefaultMonitor,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESDefaultMonitor(snes, its, fgnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESVecViewMonitor,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESVecViewMonitor(snes, its, fgnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESVecViewResidualMonitor,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESVecViewResidualMonitor(snes, its, fgnorm, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
SNESVecViewUpdateMonitor,
(SNES snes,PetscInt its,PetscReal fgnorm), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = SNESVecViewUpdateMonitor(snes, its, fgnorm, NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})


PETSC_OVERRIDE(
PetscErrorCode,
SNESSetConvergenceTest,
(SNES snes, PyObject *convtest), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (convtest == Py_None) SETERRQ(1,"Convergence Test object cannot be None");
  ctx = PyCtx_New(convtest);
  if (ctx == NULL) SETERRQ(1,"invalid Convergence Test object");
  ierr = PetscObjectComposePyCtx((PetscObject)snes, "__convtest__", ctx); CHKERRQ(ierr);
  ierr = SNESSetConvergenceTest(snes, _PySNES_ConvergenceTest,
				(void*)ctx); CHKERRQ(ierr);
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
  ierr = PetscTypeCompare((PetscObject)snes, SNESLS, &flag);CHKERRQ(ierr);
  if (flag) {
    ierr = SNESConverged_LS(snes, its, xnorm, gnorm, fnorm, 
			    reason, PETSC_NULL); CHKERRQ(ierr);
    PetscFunctionReturn(0);
  }
  ierr = PetscTypeCompare((PetscObject)snes, SNESTR, &flag);CHKERRQ(ierr);
  if (flag) {
    ierr = SNESConverged_TR(snes, its, xnorm, gnorm, fnorm, 
			    reason, PETSC_NULL); CHKERRQ(ierr);
    PetscFunctionReturn(0);
  }
  ierr = SNESConverged_LS(snes, its, xnorm, gnorm, fnorm,
			  reason, PETSC_NULL); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

#if 0
ARRAY_1D_NEW(PetscInt* nrh, PetscReal* rh[],
	     PyPetsc_REAL)

PETSC_OVERRIDE(
PetscErrorCode,
SNESGetConvergenceHistory,
(KSP ksp,PetscInt* nrh,PetscReal* rh[]), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = KSPGetResidualHistory(ksp,rh,nrh); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt* nrh,PetscReal* rh[]);


ARRAY_RAW(PetscReal rh[],
	  ARRAY_INPUT, PyPetsc_REAL)

PetscErrorCode 
SNESSetConvergenceHistory(KSP,
			  PetscReal rh[],PetscInt nrh,
			  PetscTruth reset);

%ignore KSPSetResidualHistory;

%clear PetscReal rh[];
#endif


/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Ignores                                                          */
/* ---------------------------------------------------------------- */

%ignore SNESAddOptionsChecker;

%ignore SNESList;

%ignore SNESConvergedReasons;
%ignore SNESConvergedReasons_Shifted;

%ignore SNES_Solve; 
%ignore SNES_LineSearch;
%ignore SNES_FunctionEval;
%ignore SNES_JacobianEval;

%ignore MATSNESMFCTX_COOKIE;
%ignore MATSNESMF_Mult;

%ignore _p_MatSNESMFCtx;
%ignore MatSNESMFCtx;

%ignore SNESInitializePackage;
%ignore SNESRegisterDestroy;
%ignore SNESRegisterAll;
%ignore SNESRegister;

%ignore SNESSetUpdate;
%ignore SNESDefaultUpdate;

%ignore SNESDefaultMonitor;
%ignore SNESRatioMonitor;
%ignore SNESSetRatioMonitor(SNES);
%ignore SNESVecViewMonitor;
%ignore SNESVecViewResidualMonitor;
%ignore SNESVecViewUpdateMonitor;
%ignore SNESDefaultSMonitor;
%ignore SNESLGMonitorCreate;
%ignore SNESLGMonitor;
%ignore SNESLGMonitorDestroy;

%ignore SNESConverged_LS;
%ignore SNESConverged_TR;

%ignore SNES_KSP_SetParametersEW;
%ignore SNES_KSP_SetConvergenceTestEW;

%ignore SNESLineSearchSet;
%ignore SNESLineSearchNo;
%ignore SNESLineSearchNoNorms;
%ignore SNESLineSearchCubic;
%ignore SNESLineSearchQuadratic;
%ignore SNESLineSearchSetPostCheck;
%ignore SNESLineSearchSetPreCheck;
%ignore SNESLineSearchSetParams;
%ignore SNESLineSearchGetParams;

%ignore MatSNESMFRegisterAll;
%ignore MatSNESMFRegisterDestroy;
%ignore MatSNESMFDefaultSetUmin;
%ignore MatSNESMFWPSetComputeNormA;
%ignore MatSNESMFWPSetComputeNormU;
%ignore MatCreateSNESMF;
%ignore MatCreateMF;
%ignore MatSNESMFSetBase;
%ignore MatSNESMFComputeJacobian;
%ignore MatSNESMFSetFunction;
%ignore MatSNESMFSetFunctioni;
%ignore MatSNESMFSetFunctioniBase;
%ignore MatSNESMFAddNullSpace;
%ignore MatSNESMFSetHHistory;
%ignore MatSNESMFResetHHistory;
%ignore MatSNESMFSetFunctionError;
%ignore MatSNESMFSetPeriod;
%ignore MatSNESMFGetH;
%ignore MatSNESMFKSPMonitor;
%ignore MatSNESMFSetFromOptions;
%ignore MatSNESMFCheckPositivity;
%ignore MatSNESMFSetCheckh;
%ignore MatSNESMFSetType;
%ignore MatSNESMFRegister;

%ignore MatSNESMFDSSetUmin;

%ignore  MatDAADSetSNES(Mat,SNES);
%ignore  SNESDAFormFunction;
%ignore  SNESDAComputeJacobianWithAdic;
%ignore  SNESDAComputeJacobianWithAdifor;
%ignore  SNESDAComputeJacobian;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
