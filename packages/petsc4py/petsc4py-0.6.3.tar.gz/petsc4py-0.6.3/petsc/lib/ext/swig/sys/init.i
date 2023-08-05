/* $Id$ */

%wrapper %{

static int    PyPetsc_Argc = 0;
static char** PyPetsc_Argv = NULL;

#undef  __FUNCT__
#define __FUNCT__ "PyPetscDelArgs"
static PetscErrorCode
PyPetscDelArgs(int* argc, char** argv[]) {
  int     i; 
  int    _argc = *argc;
  char** _argv = *argv;
  if (_argc && _argv) {
    for (i=0; i<_argc; i++) 
      if(_argv[i]) free(_argv[i]);
    free(_argv);
  }
  *argc = 0; *argv = NULL;
  return 0;
}

#undef  __FUNCT__
#define __FUNCT__ "PyPetscSetArgs"
static PetscErrorCode
PyPetscSetArgs(int argc, char* argv[]) {
  PyPetscDelArgs(&PyPetsc_Argc, &PyPetsc_Argv);
  if (argc && argv) {
    int    i;
    int    _argc = argc;
    char** _argv = (char**) malloc((_argc+1)*sizeof(char*));
    if (!_argv) return PETSC_ERR_MEM;
    for (i=0; i<_argc; i++) _argv[i] = strdup(argv[i] ? argv[i] : "");
    _argv[_argc] = NULL;
    /* */
    PyPetsc_Argc = _argc;
    PyPetsc_Argv = _argv;
  }
  return 0;
}

%}

/*------------------------------------------------------------------*/

%wrapper %{
static void 
PetscSetArgs(int argc, char* argv[]) { PyPetscSetArgs(argc, argv); }
%}

%include argcargv.i

%apply (int ARGC, char** ARGV) { (int argc, char* argv[]) };

%exception PetscSetArgs %{
  if (PetscInitializeCalled)
    SWIG_exception(SWIG_RuntimeError,
		   "must be called before initialization");
  $action
%}

void PetscSetArgs(int argc, char* argv[]);

%clear (int argc, char* argv[]);

/* ---------------------------------------------------------------- */

%typemap(in, noblock=1)    MPI_Comm COMM_WORLD = SWIGTYPE;
%typemap(arginit)          MPI_Comm COMM_WORLD "";
%typemap(check, noblock=1) MPI_Comm COMM_WORLD {
  if ($1 == MPI_COMM_NULL)
    SWIG_exception(SWIG_ValueError,
		   "cannot set null cummunicator as COMM_WORLD");
}

%exception PetscSetCommWorld %{
  if (PetscInitializeCalled || PetscFinalizeCalled)
    SWIG_exception(SWIG_RuntimeError,
		   "must be called before initialization");
  $action
%}

%inline %{
static void 
PetscSetCommWorld(MPI_Comm COMM_WORLD) 
{
  PETSC_COMM_WORLD = COMM_WORLD;
}
%}

%clear COMM_WORLD;

/* ---------------------------------------------------------------- */

%wrapper %{
static void 
PyPetsc_FinalizeAtExit(void) {

  PetscErrorCode ierr;
  PetscMPIInt mpi_flag_i,   mpi_flag_f;
  PetscTruth  petsc_flag_i, petsc_flag_f;

  PyPetscDelArgs(&PyPetsc_Argc, &PyPetsc_Argv);
  Py_XDECREF(_PyExc_PetscError);

  ierr = (PetscErrorCode) MPI_Initialized(&mpi_flag_i);
  ierr = (PetscErrorCode) MPI_Finalized(&mpi_flag_f);
  if (!mpi_flag_i || mpi_flag_f) return;

  ierr = PetscInitialized(&petsc_flag_i);
  ierr = PetscFinalized(&petsc_flag_f);
  if (!petsc_flag_i && !petsc_flag_f) return;
  if (petsc_flag_f) return;

  ierr = PetscPopErrorHandler();
  ierr = PetscFinalize();
  if (ierr) {
    fflush(stderr);
    fprintf(stderr, "PetscFinalize() failed [ierr: %d]\n",ierr);
    fflush(stderr);
  }
}
%}

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
PetscInitialize, (void), {
  int*    argc = &PyPetsc_Argc;
  char*** argv = &PyPetsc_Argv;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (PetscInitializeCalled) PetscFunctionReturn(0);
  if (PetscFinalizeCalled) SETERRQ(1, "PetscFinalize() already called");
  ierr = PetscInitialize(argc, argv, NULL,NULL);CHKERRQ(ierr);
  ierr = PetscPushErrorHandler(PyPetscTraceBackErrorHandler,
  			       (void*)PyPetscTraceBackError);CHKERRQ(ierr);
  ierr = PyPetscRegisterAll(PETSC_NULL);CHKERRQ(ierr);
  if (Py_AtExit(PyPetsc_FinalizeAtExit) < 0)
    PyErr_Warn(PyExc_RuntimeWarning,
	       "cannot register PetscFinalize() with Py_AtExit()");
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscFinalize, (void), {
  PetscMPIInt    flag;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PyPetscDelArgs(&PyPetsc_Argc, &PyPetsc_Argv);
  if (PetscFinalizeCalled) PetscFunctionReturn(0);
  ierr = (PetscErrorCode) MPI_Finalized(&flag);
  if (flag) PetscFunctionReturn(0);
  ierr = PetscPopErrorHandler(); CHKERRQ(ierr);
  ierr = PetscFinalize(); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PetscErrorCode PetscInitialized(PetscTruth*);
PetscErrorCode PetscFinalized(PetscTruth*);

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
