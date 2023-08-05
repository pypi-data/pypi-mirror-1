/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode
PetscViewerCreate(MPI_Comm,
		  PetscViewer* CREATE);

PetscErrorCode
PetscViewerASCIIOpen(MPI_Comm, const char[],
		     PetscViewer* CREATE);

PetscErrorCode 
PetscViewerBinaryCreate(MPI_Comm comm, PetscViewer *CREATE);

PetscErrorCode
PetscViewerBinaryOpen(MPI_Comm, const char[], PetscFileMode,
		      PetscViewer* CREATE);

PetscErrorCode
PetscViewerDrawOpen(MPI_Comm, const char[], const char[],
		    int, int, int, int,
		    PetscViewer* CREATE);

PetscErrorCode
PetscViewerStringOpen(MPI_Comm, char strbuff[], PetscInt strlen,
		      PetscViewer* CREATE);


%ignore PetscViewerCreate;
%ignore PetscViewerASCIIOpen;
%ignore PetscViewerBinaryCreate;
%ignore PetscViewerBinaryOpen;
%ignore PetscViewerDrawOpen;
%ignore PetscViewerStringOpen;

/* ---------------------------------------------------------------- */

%typemap(out, noblock=1) PetscViewer = PetscViewer OBJREF;
PetscViewer PETSC_VIEWER_STDOUT_(MPI_Comm comm);
PetscViewer PETSC_VIEWER_STDERR_(MPI_Comm comm);
PetscViewer PETSC_VIEWER_DRAW_(MPI_Comm);
PetscViewer PETSC_VIEWER_BINARY_(MPI_Comm);
%typemap(out, noblock=1) PetscViewer;

/* ---------------------------------------------------------------- */

PetscErrorCode 
PetscViewerFileGetName(PetscViewer, char**);
PetscErrorCode
PetscViewerFileSetName(PetscViewer, const char[]);
PetscErrorCode
PetscViewerFileGetMode(PetscViewer, PetscFileMode*);
PetscErrorCode 
PetscViewerFileSetMode(PetscViewer, PetscFileMode);

%ignore PetscViewerFileGetName;
%ignore PetscViewerFileSetName;
%ignore PetscViewerFileGetMode;
%ignore PetscViewerFileSetMode;

/* ---------------------------------------------------------------- */

/* forward declares XXXView() functions to define appropriate typemap
   for PetscViewer argument */

%define %PETSC_OBJECT_VIEW(PETSc_t)
PetscErrorCode 
PETSc_t##View(PETSc_t, PetscViewer OBJ_OR_NONE);
%ignore PETSc_t##View;
%enddef

%PETSC_OBJECT_VIEW( PetscObject            )
%PETSC_OBJECT_VIEW( PetscViewer            )
#if 0
%PETSC_OBJECT_VIEW( PetscRandom            )
#endif
%PETSC_OBJECT_VIEW( IS                     )
%PETSC_OBJECT_VIEW( AO                     )
%PETSC_OBJECT_VIEW( ISLocalToGlobalMapping )
%PETSC_OBJECT_VIEW( Vec                    )
%PETSC_OBJECT_VIEW( VecScatter             )
#if 0
%PETSC_OBJECT_VIEW( MatNullSpace           )
#endif
%PETSC_OBJECT_VIEW( Mat                    )
%PETSC_OBJECT_VIEW( KSP                    )
%PETSC_OBJECT_VIEW( PC                     )
%PETSC_OBJECT_VIEW( SNES                   )
%PETSC_OBJECT_VIEW( TS                     )

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore PetscViewerBinaryCreate;
%ignore PetscViewerASCIICreate;

%ignore PetscViewerList;

%ignore PetscViewerRegisterAll;
%ignore PetscViewerRegisterDestroy;
%ignore PetscViewerRegister;

%ignore PetscViewerMathematicaOpen;
%ignore PetscViewerSiloOpen;
%ignore PetscViewerMatlabOpen;

%ignore PetscViewerGetSingleton;
%ignore PetscViewerRestoreSingleton;

%ignore PetscViewerASCIIGetPointer;
%ignore PetscViewerASCIIPrintf;
%ignore PetscViewerASCIISynchronizedPrintf;

%ignore PetscViewerBinaryGetDescriptor;
%ignore PetscViewerBinaryGetInfoPointer;

%ignore PetscPLAPACKInitializePackage;
%ignore PetscPLAPACKFinalizePackage;

%ignore PetscViewerVUGetPointer;
%ignore PetscViewerVUSetMode;
%ignore PetscViewerVUSetVecSeen;
%ignore PetscViewerVUGetVecSeen;
%ignore PetscViewerVUPrintDeferred;
%ignore PetscViewerVUFlushDeferred;

%ignore PetscViewerMathematicaInitializePackage;
%ignore PetscViewerMathematicaFinalizePackage;
%ignore PetscViewerMathematicaGetName;
%ignore PetscViewerMathematicaSetName;
%ignore PetscViewerMathematicaClearName;
%ignore PetscViewerMathematicaSkipPackets;

%ignore PetscViewerSiloGetName;
%ignore PetscViewerSiloSetName;
%ignore PetscViewerSiloClearName;
%ignore PetscViewerSiloGetMeshName;
%ignore PetscViewerSiloSetMeshName;
%ignore PetscViewerSiloClearMeshName;

%ignore PetscViewerNetcdfOpen;
%ignore PetscViewerNetcdfGetID;

%ignore PetscViewerHDF4Open;
%ignore PetscViewerHDF4WriteSDS;

%ignore PETSC_VIEWER_STDOUT_;
%ignore PETSC_VIEWER_STDERR_;
%ignore PETSC_VIEWER_DRAW_;
%ignore PETSC_VIEWER_SOCKET_;
%ignore PETSC_VIEWER_BINARY_;
%ignore PETSC_VIEWER_MATLAB_;
%ignore PETSC_VIEWER_MATHEMATICA_WORLD_PRIVATE;


%ignore PetscViewerMatlabPutArray;
%ignore PetscViewerMatlabGetArray;
%ignore PetscViewerMatlabPutVariable;

%ignore PetscViewerSocketOpen;
%ignore PetscViewerSocketPutScalar;
%ignore PetscViewerSocketPutReal;
%ignore PetscViewerSocketPutInt;
%ignore PetscViewerSocketPutSparse_Private;

%ignore PetscViewersCreate;
%ignore PetscViewersDestroy;
%ignore PetscViewersGetViewer;

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
