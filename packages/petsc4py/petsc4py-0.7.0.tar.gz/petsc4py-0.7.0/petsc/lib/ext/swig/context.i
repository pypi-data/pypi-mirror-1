/* $Id$ */

/* ---------------------------------------------------------------- */
/* User Context Management for KSP, SNES and TS                     */
/* ---------------------------------------------------------------- */

%wrapper %{

#define PyCtx_CALL_FUNC PyObject_CallFunction

EXTERN_C_BEGIN

#define PyCtx_Check(ctx) \
  (((ctx) != NULL) && PyCObject_Check((ctx)))

/* destructor callback for C Objects */
static void 
_PyCtx_Del(void *ctx) { Py_XDECREF((PyObject*)ctx); }

static PyObject* 
PyCtx_New(PyObject* ctx) {
  if (ctx != NULL && ctx != Py_None) {
    PyObject* cobj = PyCObject_FromVoidPtr((void*)ctx, _PyCtx_Del);
    if (cobj != NULL) { Py_INCREF(ctx); return cobj; }
    PyErr_SetString(PyExc_MemoryError, "error creating a context object");
    return NULL;
  }
  return ctx;
}

static PyObject* 
PyCtx_Get(PyObject* cobj) {
  if (cobj != NULL) {
    if (PyCObject_Check(cobj)) {
      PyObject* pyobj = (PyObject*) PyCObject_AsVoidPtr(cobj);
      if (pyobj != NULL) return pyobj;
      PyErr_SetString(PyExc_ValueError, "null pointer for context object");
      return NULL;
    }
    PyErr_SetString(PyExc_TypeError, "invalid context object");
    return NULL;
  }
  PyErr_SetString(PyExc_ValueError, "null pointer for context object"); 
  return NULL;
}

static PetscErrorCode
_PyObj_Destroy(void* context) { Py_XDECREF((PyObject*)context); return 0; }

#undef  __FUNCT__
#define __FUNCT__ "PetscObjectComposePyCtx"
static PetscErrorCode
PetscObjectComposePyCtx(PetscObject obj, const char name[], PyObject* op) {
  PetscContainer container;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeader(obj, 1);
  PetscValidCharPointer(name, 2);
  if (op) PetscValidPointer(op, 3);
  if (op == NULL || op == Py_None) {
    ierr = PetscObjectCompose(obj, name, PETSC_NULL); CHKERRQ(ierr);
  } else {
    ierr = PetscContainerCreate(obj->comm, &container);CHKERRQ(ierr);
    ierr = PetscContainerSetUserDestroy(container, _PyObj_Destroy);CHKERRQ(ierr);
    ierr = PetscContainerSetPointer(container, (void*)op);CHKERRQ(ierr);
    ierr = PetscObjectCompose(obj, name, (PetscObject)container);CHKERRQ(ierr);
    ierr = PetscObjectDestroy((PetscObject)container);CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
}


#undef  __FUNCT__
#define __FUNCT__ "PetscObjectQueryPyCtx"
static PetscErrorCode
PetscObjectQueryPyCtx(PetscObject obj, const char name[], PyObject** op) {

  PetscObject composed;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeader(obj, 1);
  PetscValidCharPointer(name, 2);
  PetscValidPointer(op, 3);
  *op = NULL;
  ierr = PetscObjectQuery(obj, name, &composed);CHKERRQ(ierr);
  if (composed == PETSC_NULL) { *op = Py_None; PetscFunctionReturn(0); } 
  if (composed->cookie != CONTAINER_COOKIE)
    { SETERRQ(1, "composed object is not a PetscContainer"); }
  ierr = PetscContainerGetPointer((PetscContainer)composed,
				  (void**)op); CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
EXTERN_C_END
%}

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
