/* $Id$ */

%include context.i

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode 
TSCreate(MPI_Comm comm, TS* CREATE);

/* ---------------------------------------------------------------- */

PetscErrorCode
TSGetKSP(TS, KSP* NEWREF);

PetscErrorCode
TSGetSNES(TS, SNES* NEWREF);

PetscErrorCode
TSGetSolution(TS, Vec* NEWREF);

/* ---------------------------------------------------------------- */

PetscErrorCode
TSSetTime(TS, PetscReal);
%ignore TSSetTime;

PetscErrorCode
TSSolve(TS, Vec OBJ_OR_NONE);
%ignore TSSolve;

/* ---------------------------------------------------------------- */

%apply PyObject **OUTPUT { PyObject **appctx };

PETSC_OVERRIDE(
PetscErrorCode,
TSGetApplicationContext,
(TS ts, PyObject **appctx), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSGetApplicationContext(ts,(void**)&ctx);CHKERRQ(ierr);
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
TSSetApplicationContext,
(TS ts, PyObject *appctx), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(appctx);
  if (ctx == NULL) SETERRQ(1,"invalid ApplicationContext object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts,"__appctx__",ctx); CHKERRQ(ierr);
  ierr = TSSetApplicationContext(ts,(void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

%wrapper %{
/* #undef __FUNCT__   */
/* #define __FUNCT__ "PyTS_RHSBoundaryConditions" */
/* static  */
/* PetscErrorCode  */
/* _PyTS_RHSBoundaryConditions(TS ts, PetscReal t, Vec F, void *ctx) */
/* { */
/*   PyObject* bndcond  = NULL; */
/*   PyObject* retvalue = NULL; */
/*   PetscFunctionBegin; */
/*   if ((PyObject*)ctx == Py_None) PetscFunctionReturn(0); */
/*   bndcond = PyCtx_Get((PyObject*)ctx); */
/*   retvalue = PyCtx_CALL_FUNC(bndcond, "O&dO&", */
/* 			     PyTS_Ref, ts, */
/* 			     (double)t, */
/* 			     PyVec_Ref, F); */
/*   if (retvalue == NULL) goto fail; */
/*   Py_DECREF(retvalue); */
/*   PetscFunctionReturn(0); */
/*  fail: */
/*   Py_XDECREF(retvalue); */
/*   PetscFunctionReturn(1); */
/* } */

#undef __FUNCT__  
#define __FUNCT__ "PyTS_LRHSMatrix"
static 
PetscErrorCode 
_PyTS_LRHSMatrix(TS ts, PetscReal t,
		 Mat* J, Mat* P, MatStructure* matstr,
		 void *ctx)
{
  PyObject* matrix = NULL;
  PyObject* objJ     = NULL;
  PyObject* objP     = NULL;
  MatStructure ms    = DIFFERENT_NONZERO_PATTERN;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;
  if ((PyObject*)ctx == Py_None) PetscFunctionReturn(0);
  matrix  = PyCtx_Get((PyObject*)ctx);
  if (matrix == NULL) goto fail;
  objJ = PyMat_Ref(*J); if (objJ == NULL)  goto fail;
  objP = PyMat_Ref(*P); if (objP == NULL)  goto fail;
  retvalue = PyCtx_CALL_FUNC(matrix, "O&dO&O&",
			     PyTS_Ref, ts,
			     (double)t,
			     PyMat_Ref, *J,
			     PyMat_Ref, *P);
  if (retvalue == NULL) goto fail;
  
  /* get MatStructure value */
  if (retvalue != Py_None) {
    if (PyInt_Check(retvalue)) {
      ms = (MatStructure) PyInt_AS_LONG(retvalue);
      if (ms < SAME_NONZERO_PATTERN || ms > SUBSET_NONZERO_PATTERN) {
	PyErr_SetString(PyExc_ValueError,
			"TS Matrix returned an invalid "
			"value for Mat.Structure"); goto fail;
      }
    } else {
      PyErr_SetString(PyExc_TypeError,
		      "TS Matrix must return None or a valid "
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
%}

/* PETSC_OVERRIDE( */
/* PetscErrorCode, */
/* TSSetRHSBoundaryConditions, */
/* (TS ts, PyObject *bndcond), { */
/*   PyObject* ctx = NULL; */
/*   PetscErrorCode ierr; */
/*   PetscFunctionBegin; */
/*   ctx = PyCtx_New(bndcond); */
/*   if (ctx == NULL) SETERRQ(1,"invalid BoundaryConditions object"); */
/*   ierr = PetscObjectComposePyCtx((PetscObject)ts, "__rhs_bndcond__", ctx); CHKERRQ(ierr); */
/*   ierr = TSSetRHSBoundaryConditions(ts,_PyTS_RHSBoundaryConditions,(void*)ctx); CHKERRQ(ierr); */
/*   PetscFunctionReturn(0); */
/* }) */


%apply Mat OBJ_OR_NONE { Mat A, Mat P };

PETSC_OVERRIDE(
PetscErrorCode,
TSSetRHSMatrix,
(TS ts, Mat A, Mat P, PyObject *matrix), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(matrix);
  if (ctx == NULL) SETERRQ(1,"invalid Matrix object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts, "__rhs_matrix__", ctx); CHKERRQ(ierr);
  ierr = TSSetRHSMatrix(ts, A, (P!=PETSC_NULL)? P : A,
			_PyTS_LRHSMatrix, (void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSSetLHSMatrix,
(TS ts, Mat A, Mat P, PyObject *matrix), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(matrix);
  if (ctx == NULL) SETERRQ(1,"invalid Matrix object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts, "__lhs_matrix__", ctx); CHKERRQ(ierr);
  ierr = TSSetLHSMatrix(ts, A, (P!=PETSC_NULL)? P : A,
			_PyTS_LRHSMatrix, (void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear Mat A, Mat P;

/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "PyTS_RHSFunction"
static 
PetscErrorCode 
_PyTS_RHSFunction(TS ts, PetscReal t, Vec u, Vec F, void *ctx)
{
  PyObject* function = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;
  function = PyCtx_Get((PyObject*)ctx);
  if (function == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(function, "O&dO&O&",
			     PyTS_Ref,  ts,
			     (double)t,
			     PyVec_Ref, u,
			     PyVec_Ref, F);
  if (retvalue == NULL) goto fail;
  Py_DECREF(retvalue);
  PetscFunctionReturn(0);
 fail:
  Py_XDECREF(retvalue);
  PetscFunctionReturn(1);
}


#undef __FUNCT__  
#define __FUNCT__ "PyTS_RHSJacobian"
static 
PetscErrorCode 
_PyTS_RHSJacobian(TS ts,
		  PetscReal t, Vec u, 
		  Mat* J, Mat* P, MatStructure* matstr,
		  void *ctx)
{
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
  retvalue = PyCtx_CALL_FUNC(jacobian, "O&dO&O&O&",
			     PyTS_Ref, ts,
			     (double)t,
			     PyVec_Ref, u,
			     PyMat_Ref, *J,
			     PyMat_Ref, *P);
  if (retvalue == NULL) goto fail;
  
  /* get MatStructure value */
  if (retvalue != Py_None) {
    if (PyInt_Check(retvalue)) {
      ms = (MatStructure) PyInt_AS_LONG(retvalue);
      if (ms < SAME_NONZERO_PATTERN || ms > SUBSET_NONZERO_PATTERN) {
	PyErr_SetString(PyExc_ValueError,
			"TS Jacobian returned an invalid "
			"value for Mat.Structure"); goto fail;
      }
    } else {
      PyErr_SetString(PyExc_TypeError,
		      "TS Jacobian must return None or a valid "
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
%}

PETSC_OVERRIDE(
PetscErrorCode,
TSSetRHSFunction,
(TS ts, PyObject *function), {
  PyObject*      ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(function);
  if (ctx == NULL) SETERRQ(1,"invalid Function object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts, "__rhs_function__", ctx); CHKERRQ(ierr);
  ierr = TSSetRHSFunction(ts,_PyTS_RHSFunction, (void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%apply Mat* NEWREF { Mat *J, Mat *P };
%apply PyObject **OUTPUT { PyObject **jacobian };
PETSC_OVERRIDE(
PetscErrorCode,
TSGetRHSJacobian,
(TS ts, Mat *J, Mat *P, PyObject **jacobian), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSGetRHSJacobian(ts, J, P, (void**)&ctx); CHKERRQ(ierr);
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
TSSetRHSJacobian,
(TS ts, Mat A, Mat P, PyObject *jacobian), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(jacobian);
  if (ctx == NULL) SETERRQ(1,"invalid Jacobian object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts, "__rhs_jacobian__", ctx); CHKERRQ(ierr);
  ierr = TSSetRHSJacobian(ts, A, (P!=PETSC_NULL)? P : A,
			  _PyTS_RHSJacobian, (void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})
%clear Mat A, Mat P;
     

/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "PyTS_Update"
static 
PetscErrorCode
_PyTS_Update(TS ts, PetscReal t, PetscReal* dt)
{
  PyObject*      update = NULL;
  PyObject*      ret    = NULL;
  PetscReal      tstep;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  
  ierr = PetscObjectQueryPyCtx((PetscObject)ts, "__update__", &update);CHKERRQ(ierr);
  if (update == Py_None) PetscFunctionReturn(0);
  update  = PyCtx_Get(update);
  if (update == NULL) goto fail;

  if (dt) { tstep = *dt; }
  else    { ierr = TSGetTimeStep(ts,&tstep); CHKERRQ(ierr); }

  ret = PyCtx_CALL_FUNC(update, "O&dd",
			PyTS_Ref, ts, (double)t, (double)(tstep));
  if (ret == NULL) goto fail;

  if (ret != Py_None) {
    tstep = (PetscReal) PyFloat_AsDouble(ret);
    if (PyErr_Occurred()) goto fail;
    if (tstep != tstep)  {
      PyErr_SetString(PyExc_ValueError,
		      "TS Update returned a not-a-number"); goto fail;
    }
    if (dt) *dt = tstep;
  }

  Py_DECREF(ret);
  PetscFunctionReturn(0);

 fail:
  Py_XDECREF(ret);
  PetscFunctionReturn(1);
}

#undef __FUNCT__  
#define __FUNCT__ "PyTS_PreStep"
static 
PetscErrorCode
_PyTS_PreStep(TS ts) 
{
  PyObject*      prestep = NULL;
  PyObject*      ret     = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscObjectQueryPyCtx((PetscObject)ts, "__prestep__", &prestep);CHKERRQ(ierr);
  if (prestep == Py_None) PetscFunctionReturn(0);
  prestep  = PyCtx_Get((PyObject*)prestep);
  if (prestep == NULL) goto fail;
  ret = PyCtx_CALL_FUNC(prestep, "O&", PyTS_Ref, ts);
  if (ret == NULL) goto fail;
  Py_DECREF(ret);
  PetscFunctionReturn(0);
 fail:
  Py_XDECREF(ret);
  PetscFunctionReturn(1);
}

#undef __FUNCT__  
#define __FUNCT__ "PyTS_PostStep"
static 
PetscErrorCode
_PyTS_PostStep(TS ts)
{
  PyObject*      poststep = NULL;
  PyObject*      ret     = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscObjectQueryPyCtx((PetscObject)ts, "__poststep__", &poststep);CHKERRQ(ierr);
  if (poststep == Py_None) PetscFunctionReturn(0);
  poststep  = PyCtx_Get((PyObject*)poststep);
  if (poststep == NULL) goto fail;
  ret = PyCtx_CALL_FUNC(poststep, "O&", PyTS_Ref, ts);
  if (ret == NULL) goto fail;
  Py_DECREF(ret);
  PetscFunctionReturn(0);
 fail:
  Py_XDECREF(ret);
  PetscFunctionReturn(1);
}
%}

PETSC_OVERRIDE(
PetscErrorCode,
TSSetUpdate,
(TS ts, PyObject *update), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(update);
  if (ctx == NULL) SETERRQ(1,"invalid Update object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts, "__update__", ctx); CHKERRQ(ierr);
  if (ctx != Py_None) {
    ierr = TSSetUpdate(ts, _PyTS_Update); CHKERRQ(ierr);
  } else {
    ierr = TSSetUpdate(ts, TSDefaultUpdate); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSSetPreStep,
(TS ts, PyObject *prestep), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(prestep);
  if (ctx == NULL) SETERRQ(1,"invalid PreStep object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts, "__prestep__", ctx); CHKERRQ(ierr);
  if (ctx != Py_None) {
    ierr = TSSetPreStep(ts, _PyTS_PreStep); CHKERRQ(ierr);
  } else {
    ierr = TSSetPreStep(ts, TSDefaultPreStep); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSSetPostStep,
(TS ts, PyObject *poststep), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ctx = PyCtx_New(poststep);
  if (ctx == NULL) SETERRQ(1,"invalid PostStep object");
  ierr = PetscObjectComposePyCtx((PetscObject)ts, "__poststep__", ctx); CHKERRQ(ierr);
  if (ctx != Py_None) {
    ierr = TSSetPostStep(ts, _PyTS_PostStep); CHKERRQ(ierr);
  } else {
    ierr = TSSetPostStep(ts, TSDefaultPostStep); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */


%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "PyTS_Monitor"
static 
PetscErrorCode 
_PyTS_Monitor(TS ts,  PetscInt steps, PetscReal t, Vec u, void *ctx)
{
  PyObject* monitor  = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;

  monitor = PyCtx_Get((PyObject*)ctx);
  if (monitor == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(monitor, "O&ldO&",
			     PyTS_Ref, ts,
			     (long)steps,
			     (double)t,
			     PyVec_Ref, u);
  if (retvalue == NULL) goto fail;
  Py_DECREF(retvalue);
  
  PetscFunctionReturn(0);
  
 fail:
  Py_XDECREF(retvalue);
  PetscFunctionReturn(1);

}

#undef __FUNCT__  
#define __FUNCT__ "PyTS_MonitorDestroy"
static
PetscErrorCode
_PyTS_MonitorDestroy(void *ctx) {
  PetscFunctionBegin;
  if (ctx != NULL && PyCtx_Check((PyObject*)ctx)) {
    Py_DECREF((PyObject*)ctx);
  }
  PetscFunctionReturn(0);
}

%}

PETSC_OVERRIDE(
PetscErrorCode,
TSSetMonitor, 
(TS ts, PyObject *monitor), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (monitor == Py_None) SETERRQ(1,"TS Monitor cannot be None");
  ctx = PyCtx_New(monitor);
  if (ctx == NULL) SETERRQ(1,"invalid TS Monitor object");
  ierr = TSSetMonitor(ts, _PyTS_Monitor, (void*)ctx,
		      _PyTS_MonitorDestroy); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSDefaultMonitor,
(TS ts, PetscInt step, PetscReal ptime, Vec v), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSDefaultMonitor(ts, step, ptime, v, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSVecViewMonitor,
(TS ts, PetscInt step, PetscReal ptime, Vec v), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSVecViewMonitor(ts, step, ptime, v, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSLGMonitor,
(TS ts, PetscInt step, PetscReal ptime, Vec v), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSLGMonitor(ts, step, ptime, v, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */




/* ---------------------------------------------------------------- */
/* Ignores                                                          */
/* ---------------------------------------------------------------- */

%ignore TSSetSolutionBC;
%ignore TSSetSystemMatrixBC;
%ignore TSDefaultSolutionBC;
%ignore TSDefaultRhsBC;
%ignore TSDefaultSystemMatrixBC;


%ignore TSDefaultPreStep;
%ignore TSDefaultUpdate;
%ignore TSDefaultPostStep;

%ignore TS_Step;
%ignore TS_PseudoComputeTimeStep;
%ignore TS_FunctionEval;
%ignore TS_JacobianEval;

%ignore TSList;
%ignore TSRegisterAllCalled;
%ignore TSRegister;
%ignore TSRegisterAll;
%ignore TSRegisterDestroy;
%ignore TSInitializePackage;

%ignore TSSetPreStep;
%ignore TSSetUpdate;
%ignore TSSetPostStep;

%ignore TSPseudoSetTimeStep;
%ignore TSPseudoDefaultTimeStep;
%ignore TSPseudoComputeTimeStep;
%ignore TSPseudoSetVerifyTimeStep;
%ignore TSPseudoDefaultVerifyTimeStep;
%ignore TSPseudoVerifyTimeStep;
%ignore TSPseudoSetTimeStepIncrement;
%ignore TSPseudoIncrementDtFromInitialDt;

%ignore TSLGMonitorCreate;
%ignore TSLGMonitorDestroy;

%ignore TSRKSetTolerance;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */


