/* $Id$ */

/* ---------------------------------------------------------------- */
PetscErrorCode PetscViewerCreate(MPI_Comm,PetscViewer* CREATE);
PetscErrorCode PetscViewerDestroy(PetscViewer);
PetscErrorCode PetscViewerView(PetscViewer,PetscViewer);

PetscErrorCode PetscViewerASCIIOpen(MPI_Comm,const char[],PetscViewer* CREATE);
PetscErrorCode PetscViewerBinaryCreate(MPI_Comm comm,PetscViewer *CREATE);
PetscErrorCode PetscViewerBinaryOpen(MPI_Comm,const char[],PetscFileMode,PetscViewer* CREATE);
PetscErrorCode PetscViewerDrawOpen(MPI_Comm,const char[],const char[],int,int,int,int,PetscViewer* CREATE);
PetscErrorCode PetscViewerStringOpen(MPI_Comm, char[], PetscInt,PetscViewer* CREATE);

PetscErrorCode PetscViewerSetType(PetscViewer,PetscViewerType);
PetscErrorCode PetscViewerGetType(PetscViewer,PetscViewerType*);

PetscErrorCode PetscViewerSetOptionsPrefix(PetscViewer,const char[]);
PetscErrorCode PetscViewerAppendOptionsPrefix(PetscViewer,const char[]);
PetscErrorCode PetscViewerGetOptionsPrefix(PetscViewer,const char*[]);
PetscErrorCode PetscViewerSetFromOptions(PetscViewer);

PetscErrorCode PetscViewerSetUp(PetscViewer);

//PetscErrorCode PetscViewerGetSingleton(PetscViewer,PetscViewer*);
//PetscErrorCode PetscViewerRestoreSingleton(PetscViewer,PetscViewer*);

/* ---------------------------------------------------------------- */

PetscErrorCode PetscViewerSetFormat(PetscViewer,PetscViewerFormat);
PetscErrorCode PetscViewerGetFormat(PetscViewer,PetscViewerFormat*);
PetscErrorCode PetscViewerPushFormat(PetscViewer,PetscViewerFormat);
PetscErrorCode PetscViewerPopFormat(PetscViewer);

PetscErrorCode PetscViewerFlush(PetscViewer);

/* ---------------------------------------------------------------- */

PetscErrorCode PetscViewerFileGetName(PetscViewer,char**);
PetscErrorCode PetscViewerFileSetName(PetscViewer,const char[]);
PetscErrorCode PetscViewerFileGetMode(PetscViewer,PetscFileMode*);
PetscErrorCode PetscViewerFileSetMode(PetscViewer,PetscFileMode);

/* ---------------------------------------------------------------- */

PetscErrorCode PetscViewerDrawClear(PetscViewer);
PetscErrorCode PetscViewerDrawSetInfo(PetscViewer,const char[],const char[],int,int,int,int);

/* ---------------------------------------------------------------- */

%typemap(out, noblock=1) PetscViewer = PetscViewer OBJREF;
PetscViewer PETSC_VIEWER_STDOUT_(MPI_Comm comm);
PetscViewer PETSC_VIEWER_STDERR_(MPI_Comm comm);
PetscViewer PETSC_VIEWER_DRAW_(MPI_Comm);
PetscViewer PETSC_VIEWER_BINARY_(MPI_Comm);
%typemap(out, noblock=1) PetscViewer;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
