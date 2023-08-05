#define PETSCTS_DLL

#include "src/ts/tsimpl.h"        /*I "petscts.h"  I*/

PETSC_EXTERN_CXX_BEGIN
EXTERN PetscErrorCode PETSCTS_DLLEXPORT TSSetTime(TS,PetscReal);
EXTERN PetscErrorCode PETSCTS_DLLEXPORT TSSolve(TS,Vec);
PETSC_EXTERN_CXX_END

#undef __FUNCT__  
#define __FUNCT__ "TSSetTime"
/*@
   TSSetTime - Allows one to reset the time.

   Input Parameters:
+  ts - the TS context obtained from TSCreate()
-  time - the time

   Level: intermediate

.seealso: TSGetTime(), TSSetDuration()

@*/
PetscErrorCode PETSCTS_DLLEXPORT TSSetTime(TS ts, PetscReal t) 
{
  PetscFunctionBegin;
  PetscValidHeaderSpecific(ts,TS_COOKIE,1);
  ts->ptime = t;
  PetscFunctionReturn(0);
}


#undef __FUNCT__  
#define __FUNCT__ "TSSolve"
/*@
   TSSolve - Steps the requested number of timesteps.

   Collective on TS

   Input Parameter:
+  ts - the TS context obtained from TSCreate()
-  u - the solution vector, or PETSC_NULL if it was set with TSSetSolution()

   Level: beginner

.keywords: TS, timestep, solve

.seealso: TSCreate(), TSSetSolution(), TSStep()
@*/

PetscErrorCode PETSCTS_DLLEXPORT TSSolve(TS ts, Vec u)
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
