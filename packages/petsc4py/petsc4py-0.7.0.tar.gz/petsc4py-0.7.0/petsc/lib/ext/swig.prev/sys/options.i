/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode PetscOptionsCreate(void);
PetscErrorCode PetscOptionsDestroy(void);
PetscErrorCode PetscOptionsSetFromOptions(void);

PetscErrorCode PetscOptionsHasName(const char pre[],const char name[], PetscTruth *flg);
PetscErrorCode PetscOptionsSetAlias(const char inewname[], const char ioldname[]);
PetscErrorCode PetscOptionsSetValue(const char iname[], const char value[]);

%wrapper %{
#define PetscOptionsClearValue(iname) \
        ((!PetscInitializeCalled||PetscFinalizeCalled)?\
        0:PetscOptionsClearValue((iname)))
%}
PetscErrorCode PetscOptionsClearValue(const char iname[]);

%include file.i
PetscErrorCode PetscOptionsPrint(FILE *fd);

/* ---------------------------------------------------------------- */

PetscErrorCode PetscOptionsInsertString(const char in_str[]);
PetscErrorCode PetscOptionsInsertFile(const char file[]);

%apply const char** {char *copts[]};
%typemap(freearg, noblock=1) char *copts[] 
{ if ($1) PetscFree(*$1); }

PetscErrorCode PetscOptionsGetAll(char *copts[]);

%clear char *copts[];

/* ---------------------------------------------------------------- */

PetscErrorCode PetscOptionsGetTruth(const char pre[],const char name[],PetscTruth *ivalue,PetscTruth *flg);
PetscErrorCode PetscOptionsGetInt(const char pre[],const char name[],PetscInt *ivalue,PetscTruth *flg);
PetscErrorCode PetscOptionsGetReal(const char pre[],const char name[],PetscReal *dvalue,PetscTruth *flg);
PetscErrorCode PetscOptionsGetScalar(const char pre[],const char name[],PetscScalar *dvalue,PetscTruth *flg);

%typemap(in, numinputs=0, noblock=1) 
(char string[],size_t len) (char temp[257])
"$1 = temp; $2 = 256; $1[0] = 0; $1[$2] = 0;";
%typemap(argout) (char string[],size_t len) {
  PyObject* o = PyString_FromString($1);
  if (!o) %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  %append_output(o);
}

PetscErrorCode PetscOptionsGetString(const char pre[],const char name[],char string[],size_t len,PetscTruth *flg);

/* ---------------------------------------------------------------- */

%wrapper %{
#undef __FUNCT__  
#define __FUNCT__ "PetscOptionsMonitorPython"
static 
PetscErrorCode 
PetscOptionsMonitorPython(const char name[], const char value[], void *ctx)
{
  PyObject* monitor  = NULL;
  PyObject* retvalue = NULL;
  PetscFunctionBegin;

  monitor = PyCtx_Get((PyObject*)ctx);
  if (monitor == NULL) goto fail;
  retvalue = PyCtx_CALL_FUNC(monitor, "zz", name, value);
  if (retvalue == NULL) goto fail;
  Py_DECREF(retvalue);
  
  PetscFunctionReturn(0);
  
 fail:
  Py_XDECREF(retvalue);
  return 1;
}

#undef __FUNCT__  
#define __FUNCT__ "PetscOptionsMonitorPythonDestroy"
static
PetscErrorCode
PetscOptionsMonitorPythonDestroy(void *ctx) 
{
  PetscFunctionBegin;
  if (ctx != NULL && PyCtx_Check((PyObject*)ctx)) {
    Py_DECREF((PyObject*)ctx);
  }
  PetscFunctionReturn(0);
}
%}

PETSC_OVERRIDE(
PetscErrorCode,
PetscOptionsMonitorSet,(PyObject *monitor), {
  PyObject* ctx = NULL;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (monitor == Py_None) SETERRQ(1,"Options Monitor cannot be None");
  ctx = PyCtx_New(monitor);
  if (ctx == NULL) SETERRQ(1,"invalid Options Monitor object");
  ierr = PetscOptionsMonitorSet(PetscOptionsMonitorPython, (void*)ctx,
				PetscOptionsMonitorPythonDestroy); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PetscErrorCode PetscOptionsMonitorCancel(void);


%ignore PetscOptionsDefaultMonitor;
%ignore PetscOptionsMonitorDefault;

/* ---------------------------------------------------------------- */



/*
 * Local Variables:
 * mode: C
 * End:
 */


