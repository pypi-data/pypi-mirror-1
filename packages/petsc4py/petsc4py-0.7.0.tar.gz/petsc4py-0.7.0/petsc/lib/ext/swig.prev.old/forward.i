/* $Id$ */

%header %{
#if defined(PETSC_HAVE_MPIUNI)
#if !defined(MPI_Finalized)
static int MPI_Finalized(int *flag)
{
  if (flag) *flag = 0;
  return 0;
}
#endif
#endif
%}

%header %{

PETSC_EXTERN_CXX_BEGIN

EXTERN PETSC_DLLEXPORT PetscCookie CONTAINER_COOKIE;

EXTERN PetscErrorCode PETSCKSP_DLLEXPORT PCSchurGetSubKSP(PC,PetscInt*,KSP**);

EXTERN PetscErrorCode PETSCTS_DLLEXPORT TSSetTime(TS,PetscReal);
EXTERN PetscErrorCode PETSCTS_DLLEXPORT TSSolve(TS,Vec);

PETSC_EXTERN_CXX_END
%}

%header %{
#if (PETSC_VERSION_MAJOR    == 2 && \
     PETSC_VERSION_MINOR    == 3 && \
     PETSC_VERSION_SUBMINOR == 2 && \
     PETSC_VERSION_RELEASE  == 1)
#define VecStrideScale(v,start,scale) VecStrideScale(v,start,&scale)
#endif
%}

%header %{
#if (PETSC_VERSION_MAJOR    == 2 && \
     PETSC_VERSION_MINOR    == 3 && \
     PETSC_VERSION_SUBMINOR == 2 && \
     PETSC_VERSION_RELEASE  == 1)

#define PetscOptionsMonitorSet(mfun,mctx,mdestr) PetscOptionsSetMonitor(mfun,mctx,mdestr)
#define PetscOptionsMonitorCancel() PetscOptionsClearMonitor()


#define KSPMonitorSet(ksp,mfun,mctx,mdestr) KSPSetMonitor(ksp,mfun,mctx,mdestr)
#define KSPMonitorCancel(ksp) KSPClearMonitor(ksp)
#define KSPMonitorDefault KSPDefaultMonitor
#define KSPMonitorTrueResidualNorm KSPTrueMonitor
#define KSPMonitorSolution KSPVecViewMonitor
#define KSPMonitorLG KSPLGMonitor


#define SNESMonitorSet(snes,mfun,mctx,mdestr) SNESSetMonitor(snes,mfun,mctx,mdestr)
#define SNESMonitorCancel(snes) SNESClearMonitor(snes)
#define SNESMonitorDefault SNESDefaultMonitor
#define SNESMonitorResidual SNESVecViewResidualMonitor
#define SNESMonitorSolution SNESVecViewMonitor
#define SNESMonitorSolutionUpdate SNESVecViewUpdateMonitor
#define SNESMonitorLG SNESLGMonitor


#define TSMonitorSet(snes,mfun,mctx,mdestr) TSSetMonitor(snes,mfun,mctx,mdestr)
#define TSMonitorCancel(snes) TSClearMonitor(snes)
#define TSMonitorDefault TSDefaultMonitor
#define TSMonitorSolution TSVecViewMonitor
#define TSMonitorLG TSLGMonitor

#endif
%}

/*
 * Local Variables:
 * mode: C
 * End:
 */
