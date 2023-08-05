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

%header %{
#if (PETSC_VERSION_MAJOR    == 2 && \
     PETSC_VERSION_MINOR    == 3 && \
     PETSC_VERSION_SUBMINOR == 2 && \
     PETSC_VERSION_RELEASE  == 1)

#include "include/private/tsimpl.h"

static
PetscErrorCode TSSolve(TS ts, Vec u)
{
  PetscInt       steps;
  PetscReal      ptime;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(ts,TS_COOKIE,1);
  /* set solution vector if provided */
  if (u) { ierr = TSSetSolution(ts, u); CHKERRQ(ierr); }
  /* reset time step and iteration counters */
  ts->steps = 0; ts->linear_its = 0; ts->nonlinear_its = 0;
  /* steps the requested number of timesteps. */
  ierr = TSStep(ts, &steps, &ptime);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

static
PetscErrorCode TSSetTime(TS ts, PetscReal t) 
{
  PetscFunctionBegin;
  PetscValidHeaderSpecific(ts,TS_COOKIE,1);
  ts->ptime = t;
  PetscFunctionReturn(0);
}

#endif
%}

%header %{
#if (PETSC_VERSION_MAJOR    == 2 && \
     PETSC_VERSION_MINOR    == 3 && \
     PETSC_VERSION_SUBMINOR == 2 && \
     PETSC_VERSION_RELEASE  == 1)

#define PetscContainer                PetscObjectContainer
#define PetscContainerGetPointer      PetscObjectContainerGetPointer
#define PetscContainerSetPointer      PetscObjectContainerSetPointer
#define PetscContainerDestroy         PetscObjectContainerDestroy
#define PetscContainerCreate          PetscObjectContainerCreate
#define PetscContainerSetUserDestroy  PetscObjectContainerSetUserDestroy

#endif
%}
/*
 * Local Variables:
 * mode: C
 * End:
 */
