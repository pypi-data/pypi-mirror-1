/* $Id$*/

PetscErrorCode TSCreate(MPI_Comm comm, TS* CREATE);
PetscErrorCode TSDestroy(TS);

PetscErrorCode TSSetProblemType(TS,TSProblemType);
PetscErrorCode TSGetProblemType(TS,TSProblemType*);

PetscErrorCode TSGetType(TS,TSType*);
PetscErrorCode TSSetType(TS,const TSType);

PetscErrorCode TSSetOptionsPrefix(TS,const char[]);
PetscErrorCode TSAppendOptionsPrefix(TS,const char[]);
PetscErrorCode TSGetOptionsPrefix(TS,const char *[]);
PetscErrorCode TSSetFromOptions(TS);
PetscErrorCode TSSetUp(TS);

PetscErrorCode TSSetSolution(TS,Vec);
PetscErrorCode TSGetSolution(TS,Vec* NEWREF);

PetscErrorCode TSSetDuration(TS,PetscInt,PetscReal);
PetscErrorCode TSGetDuration(TS,PetscInt*,PetscReal*);

PetscErrorCode TSGetKSP(TS,KSP* NEWREF);
PetscErrorCode TSGetSNES(TS,SNES* NEWREF);

PetscErrorCode TSView(TS,PetscViewer);


PetscErrorCode TSStep(TS,PetscInt *,PetscReal*);
PetscErrorCode TSSolve(TS,Vec OPTIONAL);

PetscErrorCode TSSetInitialTimeStep(TS,PetscReal,PetscReal);
PetscErrorCode TSGetTimeStep(TS,PetscReal*);
PetscErrorCode TSGetTime(TS,PetscReal*);
PetscErrorCode TSSetTime(TS,PetscReal);
PetscErrorCode TSGetTimeStepNumber(TS,PetscInt*);
PetscErrorCode TSSetTimeStep(TS,PetscReal);


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
#undef __FUNCT__  
#define __FUNCT__ "TSAnyMatrixPython"
static 
PetscErrorCode 
TSAnyMatrixPython(TS ts, PetscReal t,
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

%apply Mat OPTIONAL { Mat A, Mat P };
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
			TSAnyMatrixPython, (void*)ctx); CHKERRQ(ierr);
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
			TSAnyMatrixPython, (void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear Mat A, Mat P;

/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "TSRHSFunctionPython"
static 
PetscErrorCode 
TSRHSFunctionPython(TS ts, PetscReal t, Vec u, Vec F, void *ctx)
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
#define __FUNCT__ "TSRHSJacobianPython"
static 
PetscErrorCode 
TSRHSJacobianPython(TS ts,
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
  ierr = TSSetRHSFunction(ts,TSRHSFunctionPython, (void*)ctx); CHKERRQ(ierr);
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


%apply Mat OPTIONAL { Mat A, Mat P };
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
			  TSRHSJacobianPython, (void*)ctx); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})
%clear Mat A, Mat P;
     

/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "TSUpdatePython"
static 
PetscErrorCode
TSUpdatePython(TS ts, PetscReal t, PetscReal* dt)
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
#define __FUNCT__ "TSPreStepPython"
static 
PetscErrorCode
TSPreStepPython(TS ts) 
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
#define __FUNCT__ "TSPostStepPython"
static 
PetscErrorCode
TSPostStepPython(TS ts)
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
    ierr = TSSetUpdate(ts, TSUpdatePython); CHKERRQ(ierr);
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
    ierr = TSSetPreStep(ts, TSPreStepPython); CHKERRQ(ierr);
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
    ierr = TSSetPostStep(ts, TSPostStepPython); CHKERRQ(ierr);
  } else {
    ierr = TSSetPostStep(ts, TSDefaultPostStep); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "TSMonitorPython"
static 
PetscErrorCode 
TSMonitorPython(TS ts,  PetscInt steps, PetscReal t, Vec u, void *ctx)
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
#define __FUNCT__ "TSMonitorPythonDestroy"
static
PetscErrorCode
TSMonitorPythonDestroy(void *ctx) {
  PetscFunctionBegin;
  if (ctx != NULL && PyCtx_Check((PyObject*)ctx)) {
    Py_DECREF((PyObject*)ctx);
  }
  PetscFunctionReturn(0);
}

%}

PETSC_OVERRIDE(
PetscErrorCode,
TSMonitorSet, 
(TS ts, PyObject *monitor), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (monitor == Py_None) SETERRQ(1,"TS Monitor cannot be None");
  ctx = PyCtx_New(monitor);
  if (ctx == NULL) SETERRQ(1,"invalid TS Monitor object");
  ierr = TSMonitorSet(ts, TSMonitorPython, (void*)ctx,
		      TSMonitorPythonDestroy); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PetscErrorCode TSMonitorCancel(TS);


PETSC_OVERRIDE(
PetscErrorCode,
TSMonitorDefault,
(TS ts, PetscInt step, PetscReal ptime, Vec v), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSMonitorDefault(ts, step, ptime, v, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSMonitorSolution,
(TS ts, PetscInt step, PetscReal ptime, Vec v), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSMonitorSolution(ts, step, ptime, v, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
TSMonitorLG,
(TS ts, PetscInt step, PetscReal ptime, Vec v), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = TSMonitorLG(ts, step, ptime, v, PETSC_NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

PetscErrorCode TSComputeRHSFunction(TS,PetscReal,Vec,Vec);
PetscErrorCode TSComputeRHSJacobian(TS,PetscReal,Vec,Mat* INOUT, Mat* INOUT, MatStructure*);

/* ---------------------------------------------------------------- */



/*
 * Local Variables:
 * mode: C
 * End:
 */
