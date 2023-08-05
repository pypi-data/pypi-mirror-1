/* $Id$ */

/* ---------------------------------------------------------------- */
PetscErrorCode PetscViewerCreate(MPI_Comm,PetscViewer* CREATE);
PetscErrorCode PetscViewerDestroy(PetscViewer);
PetscErrorCode PetscViewerView(PetscViewer,PetscViewer);

PetscErrorCode PetscViewerSetType(PetscViewer,PetscViewerType);
PetscErrorCode PetscViewerGetType(PetscViewer,PetscViewerType*);

PetscErrorCode PetscViewerASCIIOpen(MPI_Comm,const char[],PetscViewer* CREATE);
PetscErrorCode PetscViewerBinaryCreate(MPI_Comm comm,PetscViewer *CREATE);
PetscErrorCode PetscViewerBinaryOpen(MPI_Comm,const char[],PetscFileMode,PetscViewer* CREATE);
PetscErrorCode PetscViewerDrawOpen(MPI_Comm,const char[],const char[],int,int,int,int,PetscViewer* CREATE);


//PetscErrorCode PetscViewerStringOpen(MPI_Comm,char[],PetscInt,PetscViewer* CREATE);
%wrapper %{
static
PetscErrorCode VStrBuffFree(void *string)
{
  PetscErrorCode   ierr;
  PetscFunctionBegin;
  ierr = PetscFree(string);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
%}

PETSC_OVERRIDE(
PetscErrorCode,
PetscViewerStringOpen,(MPI_Comm comm, PetscInt len, PetscViewer* CREATE),{
  PetscViewer    vstr;
  char           *string;
  PetscContainer container;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  /* allocate buffer to hold string */
  if (len <= 2) SETERRQ(PETSC_ERR_ARG_OUTOFRANGE,"String must have length at least 2");
  ierr = PetscMalloc(len*sizeof(char),&string);CHKERRQ(ierr);
  ierr = PetscViewerStringOpen(comm,string,len,&vstr);CHKERRQ(ierr);
  /* cache buffer in a container */
  ierr = PetscContainerCreate(comm,&container);CHKERRQ(ierr);
  ierr = PetscContainerSetUserDestroy(container,VStrBuffFree);CHKERRQ(ierr);
  ierr = PetscContainerSetPointer(container,(void*)string);CHKERRQ(ierr);
  ierr = PetscObjectCompose((PetscObject)vstr,"__string__",(PetscObject)container);CHKERRQ(ierr);
  ierr = PetscContainerDestroy(container);CHKERRQ(ierr);
  /* output created viewer */
  *CREATE = vstr;
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscViewerStringGetString,(PetscViewer viewer, char** string),{
  PetscTruth     isstring;
  PetscContainer container;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(viewer,PETSC_VIEWER_COOKIE,1);
  PetscValidPointer(string,2);
  /* check viewer type */
  ierr = PetscTypeCompare((PetscObject)viewer,PETSC_VIEWER_STRING,&isstring);CHKERRQ(ierr);
  if (!isstring) SETERRQ(PETSC_ERR_SUP,"Only for string viewers");
  /* get cache buffer in a container */
  ierr = PetscObjectQuery((PetscObject)viewer,"__string__",(PetscObject*)&container);CHKERRQ(ierr);
  if (!container) SETERRQ(PETSC_ERR_SUP,"string viewer do not have a composed buffer");
  ierr = PetscContainerGetPointer(container,(void**)string);
  PetscFunctionReturn(0);
})


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

%typemap(out, noblock=1) PetscViewer = PetscViewer OUTREF;
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
