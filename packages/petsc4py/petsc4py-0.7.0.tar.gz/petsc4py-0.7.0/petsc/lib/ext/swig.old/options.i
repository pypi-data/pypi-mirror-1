/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode
PetscOptionsCreate(void);

PetscErrorCode 
PetscOptionsDestroy(void);

PetscErrorCode
PetscOptionsHasName(const char pre[],const char name[], PetscTruth *flg);

PetscErrorCode
PetscOptionsSetAlias(const char inewname[], const char ioldname[]);

PetscErrorCode
PetscOptionsSetValue(const char iname[], const char value[]);

%wrapper %{
#define PetscOptionsClearValue(iname) \
        ((!PetscInitializeCalled||PetscFinalizeCalled)?\
        0:PetscOptionsClearValue((iname)))
%}
PetscErrorCode
PetscOptionsClearValue(const char iname[]);

%include file.i
PetscErrorCode 
PetscOptionsPrint(FILE *fd);

/* ---------------------------------------------------------------- */

PetscErrorCode
PetscOptionsInsertString(const char in_str[]);

PetscErrorCode
PetscOptionsInsertFile(const char file[]);

%apply const char** {char *copts[]};
%typemap(freearg, noblock=1) char *copts[] 
{ if ($1) PetscFree(*$1); }

PetscErrorCode
PetscOptionsGetAll(char *copts[]);

%clear char *copts[];

/* ---------------------------------------------------------------- */

PetscErrorCode
PetscOptionsGetTruth(const char pre[],const char name[],PetscTruth *ivalue,PetscTruth *flg);

PetscErrorCode
PetscOptionsGetInt(const char pre[],const char name[],PetscInt *ivalue,PetscTruth *flg);

PetscErrorCode
PetscOptionsGetReal(const char pre[],const char name[],PetscReal *dvalue,PetscTruth *flg);

PetscErrorCode
PetscOptionsGetScalar(const char pre[],const char name[],PetscScalar *dvalue,PetscTruth *flg);

%typemap(in, numinputs=0, noblock=1) 
(char string[],size_t len) (char temp[257])
"$1 = temp; $2 = 256; $1[0] = 0; $1[$2] = 0;";
%typemap(argout) (char string[],size_t len) {
  PyObject* o = PyString_FromString($1);
  if (!o) %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  %append_output(o);
}

PetscErrorCode 
PetscOptionsGetString(const char pre[],const char name[],char string[],size_t len,PetscTruth *flg);

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */


