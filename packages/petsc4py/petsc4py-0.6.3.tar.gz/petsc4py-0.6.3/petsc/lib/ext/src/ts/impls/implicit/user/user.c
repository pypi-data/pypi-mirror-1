#define PETSCTS_DLL

/*
       Code for Timestepping with implicit backwards Euler.
*/
#include "src/ts/tsimpl.h"                /*I   "petscts.h"   I*/

typedef struct {
  PetscTruth reset;  /* reset step counter an iteration counters */
  Vec        update; /* work vector where new solution is formed */
  Vec        func;   /* work vector where F(t[i],u[i]) is stored */
} TS_User;

/*------------------------------------------------------------------------------*/

#undef __FUNCT__  
#define __FUNCT__ "TSStep_User_Nonlinear"
static PetscErrorCode TSStep_User_Nonlinear(TS ts,PetscInt *steps,PetscReal *ptime)
{
  PetscInt       i,its,lits;
  Vec            sol = ts->vec_sol;
  TS_User        *tsuser = (TS_User*)ts->data;
  PetscErrorCode ierr;
  
  PetscFunctionBegin;

  if (tsuser->reset == PETSC_TRUE) {
    ts->steps         = 0;
    ts->linear_its    = 0;
    ts->nonlinear_its = 0;
  }
  *steps = -ts->steps;
  ierr = TSMonitor(ts,ts->steps,ts->ptime,sol);CHKERRQ(ierr);
  for (i=0; i<ts->max_steps; i++) {
    ierr = (*ts->ops->update)(ts, ts->ptime, &ts->time_step);CHKERRQ(ierr);
    if ((ts->ptime + ts->time_step) > ts->max_time) break;
    ts->ptime += ts->time_step;
    ierr = VecCopy(sol,tsuser->update);CHKERRQ(ierr);
    ierr = SNESSolve(ts->snes,PETSC_NULL,tsuser->update);CHKERRQ(ierr);
    ierr = SNESGetNumberLinearIterations(ts->snes,&lits);CHKERRQ(ierr);
    ierr = SNESGetIterationNumber(ts->snes,&its);CHKERRQ(ierr);
    ts->nonlinear_its += its; ts->linear_its += lits;
    ierr = VecCopy(tsuser->update,sol);CHKERRQ(ierr);
    ts->steps++;
    ierr = TSMonitor(ts,ts->steps,ts->ptime,sol);CHKERRQ(ierr);
  }
  *steps += ts->steps;
  *ptime  = ts->ptime;

  PetscFunctionReturn(0);
}

/*------------------------------------------------------------*/
#undef __FUNCT__  
#define __FUNCT__ "TSDestroy_User"
static PetscErrorCode TSDestroy_User(TS ts)
{
  TS_User      *tsuser = (TS_User*)ts->data;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  if (tsuser->update) {ierr = VecDestroy(tsuser->update);CHKERRQ(ierr);}
  if (tsuser->func)   {ierr = VecDestroy(tsuser->func);CHKERRQ(ierr);}
  ierr = PetscFree(tsuser);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

/* ---------------------------------------------------------------- */

/* The nonlinear equation that is to be solved with SNES */
#undef __FUNCT__  
#define __FUNCT__ "TSUserFunction"
static PetscErrorCode TSUserFunction(SNES snes,Vec x,Vec y,void *ctx)
{
  TS             ts = (TS) ctx;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  /* apply user-provided function */
  ierr = TSComputeRHSFunction(ts,ts->ptime,x,y);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

/*  The Jacobian needed for SNES */
#undef __FUNCT__  
#define __FUNCT__ "TSUserJacobian"
static PetscErrorCode TSUserJacobian(SNES snes,Vec x,Mat *AA,Mat *BB,MatStructure *str,void *ctx)
{
  TS             ts = (TS) ctx;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  /* construct user's Jacobian */
  ierr = TSComputeRHSJacobian(ts,ts->ptime,x,AA,BB,str);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#undef __FUNCT__  
#define __FUNCT__ "TSSetUp_User_Nonlinear"
static PetscErrorCode TSSetUp_User_Nonlinear(TS ts)
{
  TS_User        *tsuser = (TS_User*)ts->data;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  ierr = VecDuplicate(ts->vec_sol,&tsuser->update);CHKERRQ(ierr);  
  ierr = VecDuplicate(ts->vec_sol,&tsuser->func);CHKERRQ(ierr);
  ierr = SNESSetFunction(ts->snes,tsuser->func,TSUserFunction,ts);CHKERRQ(ierr);
  ierr = SNESSetJacobian(ts->snes,ts->A,ts->B,TSUserJacobian,ts);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
/*------------------------------------------------------------*/

#undef __FUNCT__  
#define __FUNCT__ "TSSetFromOptions_User_Nonlinear"
static PetscErrorCode TSSetFromOptions_User_Nonlinear(TS ts)
{
  TS_User *tsuser = (TS_User*)ts->data;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  ierr = PetscOptionsHead("User-timestepping options");CHKERRQ(ierr);
  ierr = PetscOptionsTruth("-ts_reset","Reset time step and linear/nonlinear iteration counters to zero before timestepping","",tsuser->reset,&tsuser->reset,0);CHKERRQ(ierr);
  ierr = PetscOptionsTruth("-ts_user_reset","Reset time step and linear/nonlinear iteration counters to zero before timestepping","",tsuser->reset,&tsuser->reset,0);CHKERRQ(ierr);
  ierr = PetscOptionsTail();CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#undef __FUNCT__  
#define __FUNCT__ "TSView_User"
static PetscErrorCode TSView_User(TS ts,PetscViewer viewer)
{
  PetscFunctionBegin;
  PetscFunctionReturn(0);
}

/* ------------------------------------------------------------ */
/*MC
      TS_USER - ODE solver using 

  Level: beginner

.seealso:  TSCreate(), TS, TSSetType(), TS_EULER

M*/
EXTERN_C_BEGIN
#undef __FUNCT__  
#define __FUNCT__ "TSCreate_User"
PetscErrorCode PETSCTS_DLLEXPORT TSCreate_User(TS ts)
{
  TS_User        *tsuser;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  if (ts->problem_type == TS_LINEAR) {
    SETERRQ(PETSC_ERR_SUP,"Only for nonlinear problems");
  } else if (ts->problem_type != TS_NONLINEAR) {
    SETERRQ(PETSC_ERR_ARG_OUTOFRANGE,"No such problem type");
  }

  ts->problem_type         = TS_NONLINEAR;
  ts->ops->destroy         = TSDestroy_User;
  ts->ops->view            = TSView_User;
  ts->ops->setup           = TSSetUp_User_Nonlinear;
  ts->ops->step            = TSStep_User_Nonlinear;
  ts->ops->setfromoptions  = TSSetFromOptions_User_Nonlinear;
  
  ierr = PetscNew(TS_User,&tsuser);CHKERRQ(ierr);
  ierr = PetscLogObjectMemory(ts,sizeof(TS_User));CHKERRQ(ierr);
  ts->data = (void*)tsuser;

  tsuser->reset  = PETSC_FALSE;
  tsuser->update = PETSC_NULL;
  tsuser->func   = PETSC_NULL;

  ierr = SNESCreate(ts->comm,&ts->snes);CHKERRQ(ierr);
  ierr = PetscLogObjectParent(ts,ts->snes);CHKERRQ(ierr);

  
  PetscFunctionReturn(0);
}
EXTERN_C_END
