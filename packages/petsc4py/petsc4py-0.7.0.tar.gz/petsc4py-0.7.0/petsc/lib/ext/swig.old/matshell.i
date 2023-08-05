/* $Id$ */

/* ---------------------------------------------------------------- */
/* MatShell support on the Python side                              */
/* ---------------------------------------------------------------- */
/* - context objects are internally saved into a Python C Object.
   This is for type safety in context pointer management.
   ---------------------------------------------------------------- */

%include context.i

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

/* forward declarations*/
%wrapper %{
static PetscErrorCode _PyMatShell_Destroy(Mat mat);
static PetscErrorCode _PyMatShell_GetContext(Mat, PyObject **);
static PetscErrorCode _PyMatShell_SetContext(Mat, PyObject *);

#define PYMSH_GETCTX(MAT, CTX) \
  { PetscErrorCode __ierr = _PyMatShell_GetContext((MAT),(CTX)); CHKERRQ(__ierr); }
#define PYMSH_SETCTX(MAT, CTX) \
  { PetscErrorCode __ierr = _PyMatShell_SetContext((MAT),(CTX)); CHKERRQ(__ierr); }
%}

%apply Mat* CREATE { Mat* shell };

PETSC_OVERRIDE(
PetscErrorCode,
MatCreateShell,(MPI_Comm comm, 
		PetscInt m, PetscInt n, PetscInt M, PetscInt N,
		PyObject *ctx, Mat *shell), {
  PetscErrorCode ierr;

  PetscFunctionBegin;
  ierr = MatCreate(comm,shell);CHKERRQ(ierr);
  ierr = MatSetSizes(*shell,m,n,M,N);CHKERRQ(ierr);
  ierr = MatSetType(*shell,MATSHELL);CHKERRQ(ierr);
  ierr = MatShellSetOperation(*shell,  MATOP_DESTROY,
			      (void(*)(void))_PyMatShell_Destroy);
  CHKERRQ(ierr);
  if (ctx != NULL && ctx != Py_None) PYMSH_SETCTX(*shell, ctx);
  PetscFunctionReturn(0);
})

%clear Mat* shell;

/* ---------------------------------------------------------------- */

%apply PyObject **OUTPUT { void **ctx }
PETSC_OVERRIDE(
PetscErrorCode,
MatShellGetContext,(Mat mat, void **ctx), {
  PetscTruth flg;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscTypeCompare((PetscObject)mat,MATSHELL,&flg);CHKERRQ(ierr);
  if (!flg) SETERRQ(PETSC_ERR_ARG_WRONG, "not a shell matrix");
  PYMSH_GETCTX(mat, (PyObject **)ctx);
  PetscFunctionReturn(0);
})
%clear void **ctx;

%apply PyObject * { void *ctx }
PETSC_OVERRIDE(
PetscErrorCode,
MatShellSetContext,(Mat mat, void *ctx), {
  PetscTruth flg;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscTypeCompare((PetscObject)mat,MATSHELL,&flg);CHKERRQ(ierr);
  if (!flg) SETERRQ(PETSC_ERR_ARG_WRONG, "not a shell matrix");
  PYMSH_SETCTX(mat, (PyObject *)ctx);
  PetscFunctionReturn(0);
})
%clear void *ctx;

%ignore MatShellGetOperation;
%ignore MatShellSetOperation;

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */

%wrapper %{

#undef  __FUNCT__
#define __FUNCT__ "PyMatShell_Error"
static PetscErrorCode
_PyMatShell_Error(void) {
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
		"in method of context object\n%s: %s",
		typestr ? typestr : "",
		valuestr? valuestr: "");
  SETERRQ(1, errmesg);
  PetscFunctionReturn(1);
}

#define PYMSH_CALLMETH PyObject_CallMethod

#define PYMSH_CHKCALL(CTX, RETVAL, METHODNAME) \
 do { \
   Py_XDECREF((CTX)); \
   if ((RETVAL)) { Py_DECREF((RETVAL)); } \
   else { PetscErrorCode __ierr = _PyMatShell_Error(); CHKERRQ(__ierr); } \
 } while(0)
     
#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_NotImplemented"
static PetscErrorCode 
_PyMatShell_NotImplemented(Mat mat, ...) {
  PyObject *ctx;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MatShellGetContext(mat,(void **)&ctx);CHKERRQ(ierr);
  if (ctx == NULL)
    SETERRQ(PETSC_ERR_ARG_WRONGSTATE, 
	    "context object not set in shell matrix");
  if (!PyCObject_Check(ctx))
    SETERRQ(1, "context of shell matrix is not a Python object");
  ctx = (PyObject *) PyCObject_AsVoidPtr(ctx);
  if (ctx == NULL)
    SETERRQ(1, "null pointer for context object in shell matrix");
  /* and now generates not implemented error ... */
  SETERRQ(PETSC_ERR_SUP, "method not implemented in context object of shell matrix");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_Destroy"
static 
PetscErrorCode 
_PyMatShell_Destroy(Mat mat) {
  PyObject *ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MatShellGetContext(mat,(void **)&ctx);CHKERRQ(ierr);
  if (PyCtx_Check(ctx)) { Py_DECREF(ctx); }
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_setUpPreallocation"
static PetscErrorCode 
_PyMatShell_setUpPreallocation(Mat mat) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "setUpPreallocation", NULL);
  PYMSH_CHKCALL(ctx, ret, "setUpPreallocation");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_setOption"
static PetscErrorCode 
_PyMatShell_setOption(Mat mat, MatOption op) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "setOption", "i", (int)op);
  PYMSH_CHKCALL(ctx, ret, "setOption");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_zeroEntries"
static PetscErrorCode 
_PyMatShell_zeroEntries(Mat mat) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "zeroEntries", NULL);
  PYMSH_CHKCALL(ctx, ret, "zeroEntries");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_assemblyBegin"
static PetscErrorCode 
_PyMatShell_assemblyBegin(Mat mat, MatAssemblyType type) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "assemblyBegin", "i", (int)type);
  Py_DECREF(ctx);
  PYMSH_CHKCALL(ctx, ret, "assemblyBegin");
  Py_XDECREF(ret);
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_assemblyEnd"
static PetscErrorCode 
_PyMatShell_assemblyEnd(Mat mat, MatAssemblyType type) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "assemblyEnd", "i", (int)type);
  Py_DECREF(ctx);
  PYMSH_CHKCALL(ctx, ret, "assemblyEnd");
  Py_XDECREF(ret);
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_mult"
static PetscErrorCode 
_PyMatShell_mult(Mat mat, Vec x, Vec y) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "mult", "O&O&",
		       PyVec_Ref, x,
		       PyVec_Ref, y);
  PYMSH_CHKCALL(ctx, ret, "mult");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_multAdd"
static PetscErrorCode 
_PyMatShell_multAdd(Mat mat, Vec v1, Vec v2, Vec v3) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "multAdd", "O&O&O&",
		       PyVec_Ref, v1,
		       PyVec_Ref, v2,
		       PyVec_Ref, v3);
  PYMSH_CHKCALL(ctx, ret, "multAdd");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_multTranspose"
static PetscErrorCode 
_PyMatShell_multTranspose(Mat mat, Vec x, Vec y) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "multTranspose", "O&O&",
		       PyVec_Ref, x,
		       PyVec_Ref, y);
  PYMSH_CHKCALL(ctx, ret, "multTranspose");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_multTransposeAdd"
static PetscErrorCode 
_PyMatShell_multTransposeAdd(Mat mat, Vec v1, Vec v2, Vec v3) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "multTransposeAdd", "O&O&O&",
		       PyVec_Ref, v1,
		       PyVec_Ref, v2,
		       PyVec_Ref, v3);
  PYMSH_CHKCALL(ctx, ret, "multTransposeAdd");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_getDiagonal"
static PetscErrorCode 
_PyMatShell_getDiagonal(Mat mat, Vec v) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "getDiagonal", "O&",
		       PyVec_Ref, v);
  PYMSH_CHKCALL(ctx, ret, "getDiagonal");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_getRowMax"
static PetscErrorCode 
_PyMatShell_getRowMax(Mat mat, Vec v) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "getRowMax", "O&",
		       PyVec_Ref, v);
  PYMSH_CHKCALL(ctx, ret, "getRowMax");
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PyMatShell_diagonalScale"
static PetscErrorCode 
_PyMatShell_diagonalScale(Mat mat, Vec l, Vec r) {
  PyObject *ctx = NULL;
  PyObject *ret = NULL;
  PetscFunctionBegin;
  PYMSH_GETCTX(mat, &ctx);
  ret = PYMSH_CALLMETH(ctx, "diagonalScale", "O&O&",
		       PyVec_Ref, l,
		       PyVec_Ref, r);
  PYMSH_CHKCALL(ctx, ret, "diagonalScale");
  PetscFunctionReturn(0);
}

#undef PYMSH_CALLMETH
#undef PYMSH_CHKCALL

%}



/* getsetter for context object and mat shell operations*/
%wrapper %{
#undef  __FUNCT__
#define __FUNCT__ "PyMatShell_SetOperation"
static PetscErrorCode
_PyMatShell_SetOperation(Mat mat, 
			 MatOperation op_code, void (*op_func)(void),
			 PyObject *ctx, char op_name[]) {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (ctx == NULL || ctx == Py_None ||
      !PyObject_HasAttrString(ctx, op_name)) {
    if (op_code == MATOP_MULT || op_code == MATOP_MULT_ADD)
      op_func = (void(*)(void))_PyMatShell_NotImplemented;
    else
      op_func = (void(*)(void))NULL;
  } 
  ierr = MatShellSetOperation(mat, op_code, op_func); CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#define PYMSH_SETOP(MAT, MATOP, CTX,  NAME) \
  { ierr = _PyMatShell_SetOperation((MAT), (MATOP), \
                                    (void(*)(void)) \
                                    (_PyMatShell_##NAME), \
                                    (CTX), (#NAME)); CHKERRQ(ierr); }

#undef  __FUNCT__
#define __FUNCT__ "PyMatShell_GetContext"
static PetscErrorCode
_PyMatShell_GetContext(Mat mat, PyObject **ctx) {
  PyObject *cobj;
  PetscErrorCode ierr;
  
  PetscFunctionBegin;
  
  *ctx = NULL;
  ierr = MatShellGetContext(mat,(void **)&cobj); CHKERRQ(ierr);
  if (cobj) {
    if (PyCObject_Check(cobj)) {
      *ctx = (PyObject *) PyCObject_AsVoidPtr(cobj);
      if (*ctx) { Py_INCREF(*ctx); }
      else      { SETERRQ(1, "null pointer for context object in shell matrix"); }
    } else {
      SETERRQ(1, "context of shell matrix is not a Python object");
    }
  } else {
    PetscTruth flg;
    ierr = PetscTypeCompare((PetscObject)mat,MATSHELL,&flg);CHKERRQ(ierr);
    if (!flg) { SETERRQ(PETSC_ERR_ARG_WRONG,
			"input matrix is not a shell matrix"); }
    else      { SETERRQ(PETSC_ERR_ARG_WRONGSTATE,
			"context object not set in shell matrix"); }
  }
  
  PetscFunctionReturn(0);
} 

#undef  __FUNCT__
#define __FUNCT__ "PyMatShell_SetContext"
static PetscErrorCode
_PyMatShell_SetContext(Mat A, PyObject *ctx) 
{
  PyObject *oldctx;
  PyObject *newctx;
  PetscErrorCode ierr;
  
  PetscFunctionBegin;
  
  ierr = MatShellGetContext(A,(void **)&oldctx); CHKERRQ(ierr);
  newctx = PyCtx_New(ctx); if (newctx == Py_None) newctx = NULL;
  if (PyCtx_Check(oldctx)) { Py_DECREF(oldctx); }
  ierr = MatShellSetContext(A,(void *) newctx); CHKERRQ(ierr);

  PYMSH_SETOP(A, MATOP_SETUP_PREALLOCATION, ctx, setUpPreallocation );
  PYMSH_SETOP(A, MATOP_SET_OPTION,          ctx, setOption          );
  PYMSH_SETOP(A, MATOP_ZERO_ENTRIES,        ctx, zeroEntries        );
  PYMSH_SETOP(A, MATOP_ASSEMBLY_BEGIN,      ctx, assemblyBegin      );
  PYMSH_SETOP(A, MATOP_ASSEMBLY_END,        ctx, assemblyEnd        );
  PYMSH_SETOP(A, MATOP_MULT,                ctx, mult               );
  PYMSH_SETOP(A, MATOP_MULT_ADD,            ctx, multAdd            );
  PYMSH_SETOP(A, MATOP_MULT_TRANSPOSE,      ctx, multTranspose      );
  PYMSH_SETOP(A, MATOP_MULT_TRANSPOSE_ADD,  ctx, multTransposeAdd   );
  PYMSH_SETOP(A, MATOP_GET_DIAGONAL,        ctx, getDiagonal        );
  PYMSH_SETOP(A, MATOP_GET_ROW_MAX,         ctx, getRowMax          );
  PYMSH_SETOP(A, MATOP_DIAGONAL_SCALE,      ctx, diagonalScale      );

  PetscFunctionReturn(0);
} 

#undef PYMSH_GETCTX
#undef PYMSH_SETCTX
#undef PYMSH_SETOP

%}

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
