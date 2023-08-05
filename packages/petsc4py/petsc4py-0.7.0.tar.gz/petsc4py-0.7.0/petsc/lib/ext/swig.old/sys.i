/* $Id$ */

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
PetscGetVersion,
(int* major, int* minor, int* subminor, int* patch, 
 char** date, char** patchdate, char** authorinfo),{
  static char petsc_version_date[]       = PETSC_VERSION_DATE;
  static char petsc_version_patch_date[] = PETSC_VERSION_PATCH_DATE;
  static char petsc_author_info[]        = PETSC_AUTHOR_INFO;
  PetscFunctionBegin;
  *major      = PETSC_VERSION_MAJOR;
  *minor      = PETSC_VERSION_MINOR;
  *subminor   = PETSC_VERSION_SUBMINOR;  
  *patch      = PETSC_VERSION_PATCH;
  *date       = petsc_version_date;
  *patchdate  = petsc_version_patch_date;
  *authorinfo = petsc_author_info;
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

%apply PetscInt* INOUT { PetscInt *n, PetscInt *N }

PETSC_OVERRIDE(
PetscErrorCode,
PetscSplitOwnership,
(MPI_Comm comm, PetscInt *n, PetscInt *N), {
  PetscErrorCode ierr;
  PetscMPIInt    size;
  PetscMPIInt    rank;
  PetscFunctionBegin;
  if (*N == PETSC_DECIDE && *n == PETSC_DECIDE)
    SETERRQ(PETSC_ERR_ARG_INCOMP,
	    "Both local size and and global size cannot be PETSC_DECIDE");
  if (*N == PETSC_DECIDE) {
    ierr = MPI_Allreduce(n,N,1,MPIU_INT,MPI_SUM,comm);CHKERRQ(ierr);
  } else if (*n == PETSC_DECIDE) {
    ierr = MPI_Comm_size(comm,&size);CHKERRQ(ierr);
    ierr = MPI_Comm_rank(comm,&rank);CHKERRQ(ierr);
    *n = *N/size + ((*N % size) > rank);
  } else {
    PetscInt tmp;
    ierr = MPI_Allreduce(n,&tmp,1,MPIU_INT,MPI_SUM,comm);CHKERRQ(ierr);
    if (tmp != *N)
      SETERRQ3(PETSC_ERR_ARG_SIZ,
	       "Sum of local lengths %D does not equal global length %D, "
	       "my local length %D",tmp,*N,*n);
  }
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscSplitOwnershipBlock,
(MPI_Comm comm, PetscInt bs, PetscInt *n, PetscInt *N), {
  PetscErrorCode ierr;
  PetscMPIInt    size;
  PetscMPIInt    rank;
  PetscFunctionBegin;
  if (*N == PETSC_DECIDE && *n == PETSC_DECIDE)
    SETERRQ(PETSC_ERR_ARG_INCOMP,
	    "Both local size and and global size cannot be PETSC_DECIDE");
  if (*N == PETSC_DECIDE) {
    if (*n % bs != 0)
      SETERRQ2(PETSC_ERR_ARG_INCOMP,
	       "local size %D not divisible by block size %D",*n,bs);
    ierr = MPI_Allreduce(n,N,1,MPIU_INT,MPI_SUM,comm);CHKERRQ(ierr);
  } else if (*n == PETSC_DECIDE) {
    PetscInt Nbs = *N/bs;
    if (*N % bs != 0)
      SETERRQ2(PETSC_ERR_ARG_INCOMP,
	       "global size %D not divisible by block size %D",*N,bs);
    ierr = MPI_Comm_size(comm,&size);CHKERRQ(ierr);
    ierr = MPI_Comm_rank(comm,&rank);CHKERRQ(ierr);
    *n = bs*(Nbs/size + ((Nbs % size) > rank));
  } else {
    PetscInt tmp;
    ierr = MPI_Allreduce(n,&tmp,1,MPIU_INT,MPI_SUM,comm);CHKERRQ(ierr);
    if (tmp != *N)
      SETERRQ3(PETSC_ERR_ARG_SIZ,
	       "Sum of local lengths %D does not equal global length %D, "
	       "my local length %D",tmp,*N,*n);
  }
  PetscFunctionReturn(0);
})

%clear PetscInt *n, PetscInt *N;

/* ---------------------------------------------------------------- */

%include file.i

PETSC_OVERRIDE(
PetscErrorCode,
PetscSetStdout,(FILE* fp), {
  PetscFunctionBegin;
  if (!fp) fp = stdout;
  PETSC_STDOUT = fp;
  PetscFunctionReturn(0);
})


PETSC_OVERRIDE(
PetscErrorCode,
PetscPrintf,(MPI_Comm comm, const char message[]), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscPrintf(comm, message);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscFPrintf,(MPI_Comm comm, 
	      FILE* fp, const char message[]), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscFPrintf(comm, fp, message);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscSynchronizedPrintf,(MPI_Comm comm, const char message[]), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscSynchronizedPrintf(comm, message);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscSynchronizedFPrintf,(MPI_Comm comm, 
			  FILE* fp, const char message[]), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscSynchronizedFPrintf(comm, fp, message);
  PetscFunctionReturn(0);
})

PetscErrorCode
PetscSynchronizedFlush(MPI_Comm comm);

%ignore PetscSynchronizedFlush;

/* ---------------------------------------------------------------- */

PetscErrorCode
PetscSequentialPhaseBegin(MPI_Comm, PetscMPIInt);

%ignore PetscSequentialPhaseBegin;

PetscErrorCode
PetscSequentialPhaseEnd(MPI_Comm, PetscMPIInt);

%ignore PetscSequentialPhaseEnd;

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore PETSC_STDOUT;

%ignore PetscMPIDump;

%ignore PetscGetArchType;
%ignore PetscGetHostName;
%ignore PetscGetUserName;
%ignore PetscGetProgramName;
%ignore PetscSetProgramName;
%ignore PetscGetDate;

%ignore PetscSortInt;
%ignore PetscSortIntWithPermutation;
%ignore PetscSortStrWithPermutation;
%ignore PetscSortIntWithArray;
%ignore PetscSortIntWithScalarArray;
%ignore PetscSortReal;
%ignore PetscSortRealWithPermutation;

%ignore PetscSetDisplay;
%ignore PetscGetDisplay;

%ignore PetscGetFullPath;
%ignore PetscGetRelativePath;
%ignore PetscGetWorkingDirectory;
%ignore PetscGetRealPath;
%ignore PetscGetHomeDirectory;
%ignore PetscTestFile;
%ignore PetscTestDirectory;
%ignore PetscBinaryRead;
%ignore PetscSynchronizedBinaryRead;
%ignore PetscBinaryWrite;
%ignore PetscBinaryOpen;
%ignore PetscBinaryClose;
%ignore PetscSharedTmp;
%ignore PetscSharedWorkingDirectory;
%ignore PetscGetTmp;
%ignore PetscFileRetrieve;
%ignore PetscLs;
%ignore PetscDLLibraryCCAAppend;

%ignore PETSC_BINARY_INT_SIZE;
%ignore PETSC_BINARY_FLOAT_SIZE;
%ignore PETSC_BINARY_CHAR_SIZE;
%ignore PETSC_BINARY_SHORT_SIZE;
%ignore PETSC_BINARY_DOUBLE_SIZE;
%ignore PETSC_BINARY_SCALAR_SIZE;

%ignore PetscBinarySeekType;
%ignore PetscBinarySeek;
%ignore PetscSynchronizedBinarySeek;

%ignore PetscSetDebugger;
%ignore PetscSetDefaultDebugger;
%ignore PetscSetDebuggerFromString;
%ignore PetscAttachDebugger;
%ignore PetscStopForDebugger;

%ignore PetscGatherNumberOfMessages;
%ignore PetscGatherMessageLengths;
%ignore PetscGatherMessageLengths2;
%ignore PetscPostIrecvInt;
%ignore PetscPostIrecvScalar;

%ignore PetscSSEIsEnabled;

%ignore PetscMallocDump;
%ignore PetscMallocDumpLog;
%ignore PetscMallocGetCurrentUsage;
%ignore PetscMallocGetMaximumUsage;
%ignore PetscMallocDebug;
%ignore PetscMallocValidate;
%ignore PetscMallocSetDumpLog;

%ignore PetscMemoryGetCurrentUsage;
%ignore PetscMemoryGetMaximumUsage;
%ignore PetscMemorySetGetMaximumUsage;
%ignore PetscMemoryShowUsage;


/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */


