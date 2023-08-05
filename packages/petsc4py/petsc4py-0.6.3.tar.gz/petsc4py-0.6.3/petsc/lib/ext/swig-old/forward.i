/* $Id$ */

%header %{
#if defined(PETSC_HAVE_MPIUNI)
#if !defined(MPI_Finalized)
#define MPI_Finalized(flag) (((flag)?(*(flag)=0):0),0)
#endif
#endif
%}

%header %{
PETSC_EXTERN_CXX_BEGIN

EXTERN PETSC_DLLEXPORT PetscCookie CONTAINER_COOKIE;

EXTERN PetscErrorCode PETSC_DLLEXPORT PetscObjectSetState(PetscObject,PetscInt);
EXTERN PetscErrorCode PETSC_DLLEXPORT PetscViewerFileGetMode(PetscViewer viewer,PetscFileMode*);

EXTERN PetscErrorCode PETSCKSP_DLLEXPORT PCSchurGetSubKSP(PC,PetscInt*,KSP**);

EXTERN PetscErrorCode PETSCTS_DLLEXPORT TSSetTime(TS,PetscReal);
EXTERN PetscErrorCode PETSCTS_DLLEXPORT TSSolve(TS,Vec);

PETSC_EXTERN_CXX_END
%}


#if 0 // corrected in swig-1.3.30
/* bad prototypes! this should be reported to SWIG team ... */
%header %{
#if !defined(__cplusplus)
SWIGINTERN swig_type_info* SWIG_pchar_descriptor(void);
SWIGINTERN PyObject*       SWIG_globals(void);
#endif
%}
#endif

/*
 * Local Variables:
 * mode: C
 * End:
 */
