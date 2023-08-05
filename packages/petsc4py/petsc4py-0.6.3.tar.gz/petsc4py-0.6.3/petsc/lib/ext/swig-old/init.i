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

  MPI_Initialized(&mpi_flag_i);
  MPI_Finalized(&mpi_flag_f);
  if (!mpi_flag_i || mpi_flag_f) return;

  PetscInitialized(&petsc_flag_i);
  PetscFinalized(&petsc_flag_f);
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
  MPI_Finalized(&flag);
  if (flag) PetscFunctionReturn(0);
  ierr = PetscPopErrorHandler(); CHKERRQ(ierr);
  ierr = PetscFinalize(); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%ignore PetscInitializePackage;
%ignore PetscInitializeNoArguments;
%ignore PetscInitializeFortran;
%ignore PetscInitializeCalled;
%ignore PetscFinalizeCalled;
%ignore PetscGetArgs;
%ignore PetscEnd;


/* ---------------------------------------------------------------- */

%ignore PetscSetHelpVersionFunctions;

%ignore PetscTrMalloc;
%ignore PetscTrFree;
%ignore PetscSetMalloc;
%ignore PetscClearMalloc;
%ignore PetscTrDump;
%ignore PetscTrSpace;
%ignore PetscTrValid;
%ignore PetscTrDebug;
%ignore PetscTrLog;
%ignore PetscTrLogDump;
%ignore PetscGetResidentSetSize;

%ignore PetscDataType;
%ignore PetscDataTypeToMPIDataType;
%ignore PetscDataTypeGetSize;
%ignore PetscDataTypeGetName;

%ignore PetscMemcpy;
%ignore PetscBitMemcpy;
%ignore PetscMemmove;
%ignore PetscMemzero;
%ignore PetscMemcmp;
%ignore PetscStrlen;
%ignore PetscStrcmp;
%ignore PetscStrgrt;
%ignore PetscStrcasecmp;
%ignore PetscStrncmp;
%ignore PetscStrcpy;
%ignore PetscStrcat;
%ignore PetscStrncat;
%ignore PetscStrncpy;
%ignore PetscStrchr;
%ignore PetscStrtolower;
%ignore PetscStrrchr;
%ignore PetscStrstr;
%ignore PetscStrrstr;
%ignore PetscStrallocpy;
%ignore PetscStrreplace;

%ignore PetscToken;
%ignore PetscTokenCreate;
%ignore PetscTokenFind;
%ignore PetscTokenDestroy;

%ignore PetscMaxSum_Op;
%ignore PetscSum_Op;
%ignore PetscMaxSum;

%ignore PetscShowMemoryUsage;

%ignore PetscOListDestroy;
%ignore PetscOListFind;
%ignore PetscOListReverseFind;
%ignore PetscOListAdd;
%ignore PetscOListDuplicate;

%ignore PetscFListAdd;
%ignore PetscFListDestroy;
%ignore PetscFListFind;
%ignore PetscFListPrintTypes;
%ignore PetscFListDuplicate;
%ignore PetscFListView;
%ignore PetscFListConcat;
%ignore PetscFListGet;

%ignore DLLibrariesLoaded;
%ignore PetscDLLibraryRetrieve;
%ignore PetscDLLibraryOpen;
%ignore PetscDLLibrarySym;
%ignore PetscDLLibraryAppend;
%ignore PetscDLLibraryPrepend;
%ignore PetscDLLibraryClose;
%ignore PetscDLLibraryPrintPath;
%ignore PetscDLLibraryGetInfo;

%ignore PetscLanguage;
%ignore PetscObjectComposeLanguage;
%ignore PetscObjectQueryLanguage;

%ignore PetscFixFilename;
%ignore PetscFOpen;
%ignore PetscFClose;
%ignore PetscFPrintf;
%ignore PetscPrintf;
%ignore PetscVSNPrintf;
%ignore PetscVFPrintf;

%ignore PetscErrorPrintf;
%ignore PetscHelpPrintf;

%ignore PetscPOpen;
%ignore PetscPClose;
%ignore PetscSynchronizedFGets;
%ignore PetscStartMatlab;
%ignore PetscStartJava;
%ignore PetscGetPetscDir;

%ignore PetscPopUpSelect;

%ignore PetscObjectContainerGetPointer;
%ignore PetscObjectContainerSetPointer;
%ignore PetscObjectContainerDestroy;
%ignore PetscObjectContainerCreate;

%ignore PetscCompare;
%ignore PetscCompareDouble;
%ignore PetscCompareScalar;
%ignore PetscCompareInt;

%ignore PetscIntView;
%ignore PetscRealView;
%ignore PetscScalarView;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
