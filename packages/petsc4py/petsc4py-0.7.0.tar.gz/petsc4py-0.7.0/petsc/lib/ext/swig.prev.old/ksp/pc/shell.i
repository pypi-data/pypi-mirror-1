/* $Id$ */

/* forward declarations*/
%wrapper %{
static PetscErrorCode _PyPCShell_GetContext(PC, PyObject**);
static PetscErrorCode _PyPCShell_SetContext(PC, PyObject*);

#undef PYPCSH_GETCTX
#define PYPCSH_GETCTX(pc, CTX) \
  { ierr = _PyPCShell_GetContext((pc),(CTX)); CHKERRQ(ierr); }
#undef PYPCSH_SETCTX
#define PYPCSH_SETCTX(pc, CTX) \
  { ierr = _PyPCShell_SetContext((pc),(CTX)); CHKERRQ(ierr); }
%}

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "PyPCShell_Destroy"
static 
PetscErrorCode 
_PyPCShell_Destroy(void* ctx) {
  PyObject* op = (PyObject*) ctx;
  if (PyCtx_Check(op)) { Py_DECREF(op); }
  return 0;
}
%}

%apply PC* CREATE { PC* shell };
PETSC_OVERRIDE(
PetscErrorCode,
PCCreateShell,(MPI_Comm comm, PyObject* ctx, PC* shell), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PCCreate(comm,shell); CHKERRQ(ierr);
  ierr = PCSetType(*shell,PCSHELL); CHKERRQ(ierr);
  PYPCSH_SETCTX(*shell, ctx);
  PetscFunctionReturn(0);
})
%clear PC* shell;

PETSC_OVERRIDE(
PetscErrorCode,
PCShellGetName, (PC pc, const char* name[]), {
  char* cname;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PCShellGetName(pc, &cname); CHKERRQ(ierr);
  *name = cname;
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PCShellSetName,(PC pc, const char name[]), {
  PetscTruth flg;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscTypeCompare((PetscObject)pc,PCSHELL,&flg);CHKERRQ(ierr);
  if (!flg) SETERRQ(PETSC_ERR_ARG_WRONG, "not a shell preconditioner");
  ierr = PCShellSetName(pc, name); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%apply PyObject** OUTPUT { PyObject** ctx }
PETSC_OVERRIDE(
PetscErrorCode,
PCShellGetContext,(PC pc, PyObject** ctx), {
  PetscTruth flg;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscTypeCompare((PetscObject)pc,PCSHELL,&flg);CHKERRQ(ierr);
  if (!flg) SETERRQ(PETSC_ERR_ARG_WRONG, "not a shell preconditioner");
  PYPCSH_GETCTX(pc, ctx);
  PetscFunctionReturn(0);
})
%clear PyObject** ctx;


PETSC_OVERRIDE(
PetscErrorCode,
PCShellSetContext,(PC pc, PyObject* ctx), {
  PetscTruth flg;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscTypeCompare((PetscObject)pc,PCSHELL,&flg);CHKERRQ(ierr);
  if (!flg) SETERRQ(PETSC_ERR_ARG_WRONG, "not a shell preconditioner");
  PYPCSH_SETCTX(pc, ctx);
  PetscFunctionReturn(0);
})


/* ---------------------------------------------------------------- */

%wrapper %{

#undef __FUNCT__
#define __FUNCT__ "PyPCShell_Error"
static PetscErrorCode
_PyPCShell_Error(const char* method) {
  PyObject *ptype, *pvalue, *ptrbck;
  PyObject *stype = NULL, *svalue = NULL;
  char *typestr = NULL, *valuestr = NULL;
  char errmesg[256];
  PetscFunctionBegin;
  PyErr_Fetch(&ptype, &pvalue, &ptrbck);
  if (ptype && (stype = PyObject_Str(ptype)))
    typestr = PyString_AS_STRING(stype);
  if (pvalue && (svalue = PyObject_Str(pvalue)))
    valuestr = PyString_AS_STRING(svalue);
  Py_XDECREF(stype);
  Py_XDECREF(svalue);
  PyErr_Restore(ptype, pvalue, ptrbck);
  PyOS_snprintf(errmesg, sizeof(errmesg),
		"in method '%s' of context object\n%s: %s",
		method ? method : "<unknown>",
		typestr ? typestr : "",
		valuestr? valuestr: "");
  SETERRQ(1, errmesg);
  PetscFunctionReturn(0);
}

#define PYPCSHCTX_GET(PYOBJ, CTX) \
{ \
  if (!CTX) SETERRQ(1, "context object not set"); \
  if (!PyCObject_Check((PyObject*)CTX)) \
    SETERRQ(1, "context object is not a Python object"); \
  PYOBJ = (PyObject*) PyCObject_AsVoidPtr((PyObject*)CTX); \
  if (!PYOBJ) SETERRQ(1, "null pointer for context object"); \
  Py_INCREF(PYOBJ); \
}

#define PYPCSH_CALLMETH PyObject_CallMethod

#define PYPCSH_CHKCALL(CTX, RETVAL, METHODNAME) \
 do { \
   Py_XDECREF((CTX)); \
   if ((RETVAL)) { Py_DECREF((RETVAL)); } \
   else { PetscErrorCode __ierr = _PyPCShell_Error((METHODNAME)); CHKERRQ(__ierr); } \
 } while(0)

#undef __FUNCT__  
#define __FUNCT__ "PyPCShell_view"
static PetscErrorCode 
_PyPCShell_view(void* ctx, PetscViewer viewer) {
  PyObject* obj = NULL;
  PyObject* ret = NULL;
  PetscFunctionBegin;
  PYPCSHCTX_GET(obj, ctx);
  ret = PYPCSH_CALLMETH(obj, "view", "O&",
			PyPetscViewer_Ref, viewer);
  PYPCSH_CHKCALL(obj, ret, "view");
  PetscFunctionReturn(0);
}


#undef __FUNCT__  
#define __FUNCT__ "PyPCShell_setUp"
static PetscErrorCode 
_PyPCShell_setUp(void* ctx) {
  PyObject* obj = NULL;
  PyObject* ret = NULL;
  PetscFunctionBegin;
  PYPCSHCTX_GET(obj, ctx);
  ret = PYPCSH_CALLMETH(obj, "setUp", NULL);
  PYPCSH_CHKCALL(obj, ret, "setUp");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__
#define __FUNCT__ "PyPCShell_preSolve"
static PetscErrorCode 
_PyPCShell_preSolve(void* ctx, KSP ksp, Vec b, Vec x) {
  PyObject* obj = NULL;
  PyObject* ret = NULL;
  PetscFunctionBegin;
  PYPCSHCTX_GET(obj, ctx);
  ret = PYPCSH_CALLMETH(obj, "preSolve", "O&O&O&",
			PyKSP_Ref, ksp,
			PyVec_Ref, b,
			PyVec_Ref, x);
  PYPCSH_CHKCALL(obj, ret, "preSolve");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__
#define __FUNCT__ "PyPCShell_postSolve"
static PetscErrorCode 
_PyPCShell_postSolve(void* ctx, KSP ksp, Vec b, Vec x) {
  PyObject* obj = NULL;
  PyObject* ret = NULL;
  PetscFunctionBegin;
  PYPCSHCTX_GET(obj, ctx);
  ret = PYPCSH_CALLMETH(obj, "postSolve", "O&O&O&",
			PyKSP_Ref, ksp,
			PyVec_Ref, b,
			PyVec_Ref, x);
  PYPCSH_CHKCALL(obj, ret, "postSolve");
  PetscFunctionReturn(0);
}

#undef __FUNCT__  
#define __FUNCT__ "PyPCShell_apply"
static PetscErrorCode 
_PyPCShell_apply(void* ctx, Vec x, Vec y) {
  PyObject* obj = NULL;
  PyObject* ret = NULL;
  PetscFunctionBegin;
  PYPCSHCTX_GET(obj, ctx);
  ret = PYPCSH_CALLMETH(obj, "apply", "O&O&",
			PyVec_Ref, x,
			PyVec_Ref, y);
  PYPCSH_CHKCALL(obj, ret, "apply");
  PetscFunctionReturn(0);
}

#undef __FUNCT__  
#define __FUNCT__ "PyPCShell_applyTranspose"
static PetscErrorCode 
_PyPCShell_applyTranspose(void* ctx, Vec x, Vec y) {
  PyObject* obj = NULL;
  PyObject* ret = NULL;
  PetscFunctionBegin;
  PYPCSHCTX_GET(obj, ctx);
  ret = PYPCSH_CALLMETH(obj, "applyTranspose", "O&O&",
			PyVec_Ref, x,
			PyVec_Ref, y);
  PYPCSH_CHKCALL(obj, ret, "applyTranspose");
  PetscFunctionReturn(0);
}


%}


%wrapper %{

#undef __FUNCT__
#define __FUNCT__ "PyPCShell_GetContext"
static PetscErrorCode
_PyPCShell_GetContext(PC pc, PyObject** ctx) {
  PyObject* cobj;
  PetscErrorCode ierr;
  
  PetscFunctionBegin;
  
  *ctx = NULL;
  ierr = PCShellGetContext(pc,(void**)&cobj); CHKERRQ(ierr);
  if (cobj) {
    if (PyCObject_Check(cobj)) {
      *ctx = (PyObject*) PyCObject_AsVoidPtr(cobj);
      if (*ctx) { Py_INCREF(*ctx); }
      else      { SETERRQ(1, "null pointer for context object in shell preconditioner"); }
    } else {
      SETERRQ(1, "context of shell preconditioner is not a Python object");
    }
  } else {
    PetscTruth flg;
    ierr = PetscTypeCompare((PetscObject)pc,PCSHELL,&flg);CHKERRQ(ierr);
    if (!flg) { SETERRQ(PETSC_ERR_ARG_WRONG,
			"input preconditioner is not a shell preconditioner"); }
    else      { SETERRQ(PETSC_ERR_ARG_WRONGSTATE,
			"context object not set in shell preconditioner"); }
  }
  
  PetscFunctionReturn(0);
} 

#undef PYPCSH_SETFUNC
#define PYPCSH_SETFUNC(pc, CTX,  PYNAME, CNAME, ARGS) \
{ \
  PetscErrorCode (*func)ARGS; \
  if (ctx == NULL || ctx == Py_None || !PyObject_HasAttrString(ctx, #PYNAME)) \
    { func = (PetscErrorCode(*)ARGS)NULL; } \
  else  \
    { func = (PetscErrorCode(*)ARGS)_PyPCShell_##PYNAME; } \
  ierr = PCShellSet##CNAME(pc, func); CHKERRQ(ierr); \
}


#undef __FUNCT__
#define __FUNCT__ "PyPCShell_SetContext"
static PetscErrorCode
_PyPCShell_SetContext(PC pc, PyObject* ctx) 
{
  PyObject* oldctx;
  PyObject* newctx;
  PetscErrorCode ierr;
  
  PetscFunctionBegin;
  
  ierr = PCShellGetContext(pc,(void**)&oldctx); CHKERRQ(ierr);
  newctx = PyCtx_New(ctx); if (newctx == Py_None) newctx = NULL;
  if (PyCtx_Check(oldctx)) { Py_DECREF(oldctx); }
  ierr = PCShellSetContext(pc,(void*)newctx);CHKERRQ(ierr);
  ierr = PCShellSetDestroy(pc,newctx?_PyPCShell_Destroy:NULL);CHKERRQ(ierr);

  PYPCSH_SETFUNC(pc, ctx, view,           View,           (void*,PetscViewer));
  PYPCSH_SETFUNC(pc, ctx, setUp,          SetUp,          (void*)            );
  PYPCSH_SETFUNC(pc, ctx, preSolve,       PreSolve,       (void*,KSP,Vec,Vec));
  PYPCSH_SETFUNC(pc, ctx, postSolve,      PostSolve,      (void*,KSP,Vec,Vec));
  PYPCSH_SETFUNC(pc, ctx, apply,          Apply,          (void*,Vec,Vec)    );
  PYPCSH_SETFUNC(pc, ctx, applyTranspose, ApplyTranspose, (void*,Vec,Vec)    );
  /*
  PYPCSH_SETFUNC(pc, ctx, applyRichardson, ApplyRichardson, (void*,Vec,Vec,Vec,PetscReal,PetscReal,PetscReal,PetscInt));
  */

  PetscFunctionReturn(0);
} 

#undef PYPCSH_SETFUNC

%}


/*
 * Local Variables:
 * mode: C
 * End:
 */
