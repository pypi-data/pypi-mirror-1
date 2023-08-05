#define PETSCSNES_DLL

#include "src/snes/impls/full/full.h"

/*
     Checks if J^T F = 0 which implies we've found a local minimum of the function,
    but not a zero. In the case when one cannot compute J^T F we use the fact that
    0 = (J^T F)^T W = F^T J W iff W not in the null space of J. Thanks for Jorge More 
    for this trick.
*/ 
#undef __FUNCT__  
#define __FUNCT__ "SNESLSCheckLocalMin_Private"
PetscErrorCode SNESLSCheckLocalMin_Private(Mat A,Vec F,Vec W,PetscReal fnorm,PetscTruth *ismin)
{
  PetscReal      a1;
  PetscErrorCode ierr;
  PetscTruth     hastranspose;

  PetscFunctionBegin;
  *ismin = PETSC_FALSE;
  ierr = MatHasOperation(A,MATOP_MULT_TRANSPOSE,&hastranspose);CHKERRQ(ierr);
  if (hastranspose) {
    /* Compute || J^T F|| */
    ierr = MatMultTranspose(A,F,W);CHKERRQ(ierr);
    ierr = VecNorm(W,NORM_2,&a1);CHKERRQ(ierr);
    ierr = PetscInfo1(0,"|| J^T F|| %G near zero implies found a local minimum\n",a1/fnorm);CHKERRQ(ierr);
    if (a1/fnorm < 1.e-4) *ismin = PETSC_TRUE;
  } else {
    Vec         work;
    PetscScalar result;
    PetscReal   wnorm;

    ierr = VecSetRandom(W,PETSC_NULL);CHKERRQ(ierr);
    ierr = VecNorm(W,NORM_2,&wnorm);CHKERRQ(ierr);
    ierr = VecDuplicate(W,&work);CHKERRQ(ierr);
    ierr = MatMult(A,W,work);CHKERRQ(ierr);
    ierr = VecDot(F,work,&result);CHKERRQ(ierr);
    ierr = VecDestroy(work);CHKERRQ(ierr);
    a1   = PetscAbsScalar(result)/(fnorm*wnorm);
    ierr = PetscInfo1(0,"(F^T J random)/(|| F ||*||random|| %G near zero implies found a local minimum\n",a1);CHKERRQ(ierr);
    if (a1 < 1.e-4) *ismin = PETSC_TRUE;
  }
  PetscFunctionReturn(0);
}

/*
     Checks if J^T(F - J*X) = 0 
*/ 
#undef __FUNCT__  
#define __FUNCT__ "SNESLSCheckResidual_Private"
PetscErrorCode SNESLSCheckResidual_Private(Mat A,Vec F,Vec X,Vec W1,Vec W2)
{
  PetscReal      a1,a2;
  PetscErrorCode ierr;
  PetscTruth     hastranspose;

  PetscFunctionBegin;
  ierr = MatHasOperation(A,MATOP_MULT_TRANSPOSE,&hastranspose);CHKERRQ(ierr);
  if (hastranspose) {
    ierr = MatMult(A,X,W1);CHKERRQ(ierr);
    ierr = VecAXPY(W1,-1.0,F);CHKERRQ(ierr);

    /* Compute || J^T W|| */
    ierr = MatMultTranspose(A,W1,W2);CHKERRQ(ierr);
    ierr = VecNorm(W1,NORM_2,&a1);CHKERRQ(ierr);
    ierr = VecNorm(W2,NORM_2,&a2);CHKERRQ(ierr);
    if (a1) {
      ierr = PetscInfo1(0,"||J^T(F-Ax)||/||F-AX|| %G near zero implies inconsistent rhs\n",a2/a1);CHKERRQ(ierr);
    }
  }
  PetscFunctionReturn(0);
}

/*  -------------------------------------------------------------------- 

     This file implements a truncated Newton method with a line search,
     for solving a system of nonlinear equations, using the KSP, Vec, 
     and Mat interfaces for linear solvers, vectors, and matrices, 
     respectively.

     The following basic routines are required for each nonlinear solver:
          SNESCreate_XXX()          - Creates a nonlinear solver context
          SNESSetFromOptions_XXX()  - Sets runtime options
          SNESSolve_XXX()           - Solves the nonlinear system
          SNESDestroy_XXX()         - Destroys the nonlinear solver context
     The suffix "_XXX" denotes a particular implementation, in this case
     we use _Full (e.g., SNESCreate_Full, SNESSolve_Full) for solving
     systems of nonlinear equations with a line search (LS) method.
     These routines are actually called via the common user interface
     routines SNESCreate(), SNESSetFromOptions(), SNESSolve(), and 
     SNESDestroy(), so the application code interface remains identical 
     for all nonlinear solvers.

     Another key routine is:
          SNESSetUp_XXX()           - Prepares for the use of a nonlinear solver
     by setting data structures and options.   The interface routine SNESSetUp()
     is not usually called directly by the user, but instead is called by
     SNESSolve() if necessary.

     Additional basic routines are:
          SNESView_XXX()            - Prints details of runtime options that
                                      have actually been used.
     These are called by application codes via the interface routines
     SNESView().

     The various types of solvers (preconditioners, Krylov subspace methods,
     nonlinear solvers, timesteppers) are all organized similarly, so the
     above description applies to these categories also.  

    -------------------------------------------------------------------- */
/*
   SNESSolve_Full - Solves a nonlinear system with a truncated Newton
   method with a line search.

   Input Parameters:
.  snes - the SNES context

   Output Parameter:
.  outits - number of iterations until termination

   Application Interface Routine: SNESSolve()

   Notes:
   This implements essentially a truncated Newton method with a
   line search.  By default a cubic backtracking line search 
   is employed, as described in the text "Numerical Methods for
   Unconstrained Optimization and Nonlinear Equations" by Dennis 
   and Schnabel.
*/
#undef __FUNCT__  
#define __FUNCT__ "SNESSolve_Full"
PetscErrorCode SNESSolve_Full(SNES snes)
{ 
  SNES_Full            *neP = (SNES_Full*)snes->data;
  PetscErrorCode     ierr;
  PetscInt           maxits,i,lits;
  PetscTruth         lssucceed;
  MatStructure       flg = DIFFERENT_NONZERO_PATTERN;
  PetscReal          fnorm,gnorm,xnorm,ynorm;
  Vec                Y,X,F,G,W,TMP;
  KSPConvergedReason kspreason;

  PetscFunctionBegin;
  snes->numFailures            = 0;
  snes->numLinearSolveFailures = 0;
  snes->reason                 = SNES_CONVERGED_ITERATING;

  maxits	= snes->max_its;	/* maximum number of iterations */
  X		= snes->vec_sol;	/* solution vector */
  F		= snes->vec_func;	/* residual vector */
  Y		= snes->work[0];	/* work vectors */
  G		= snes->work[1];
  W		= snes->work[2];

  ierr = PetscObjectTakeAccess(snes);CHKERRQ(ierr);
  snes->iter = 0;
  ierr = PetscObjectGrantAccess(snes);CHKERRQ(ierr);
  ierr = SNESComputeFunction(snes,X,F);CHKERRQ(ierr);
  ierr = VecNorm(F,NORM_2,&fnorm);CHKERRQ(ierr);	/* fnorm <- ||F||  */
  if (fnorm != fnorm) SETERRQ(PETSC_ERR_FP,"User provided compute function generated a Not-a-Number");
  ierr = PetscObjectTakeAccess(snes);CHKERRQ(ierr);
  snes->norm = fnorm;
  ierr = PetscObjectGrantAccess(snes);CHKERRQ(ierr);
  SNESLogConvHistory(snes,fnorm,0);
  SNESMonitor(snes,0,fnorm);
  ierr = (*snes->ops->converged)(snes,snes->iter,0.0,0.0,fnorm,&snes->reason,snes->cnvP);CHKERRQ(ierr);
  if (snes->reason) PetscFunctionReturn(0);

  for (i=0; i<maxits; i++) {

    /* Call general purpose update function */
    if (snes->ops->update) {
      ierr = (*snes->ops->update)(snes, snes->iter);CHKERRQ(ierr);
    }

    /* Solve J Y = F, where J is Jacobian matrix */
    ierr = SNESComputeJacobian(snes,X,&snes->jacobian,&snes->jacobian_pre,&flg);CHKERRQ(ierr);
    ierr = KSPSetOperators(snes->ksp,snes->jacobian,snes->jacobian_pre,flg);CHKERRQ(ierr);
    ierr = KSPSolve(snes->ksp,F,Y);CHKERRQ(ierr);
    ierr = KSPGetConvergedReason(snes->ksp,&kspreason);CHKERRQ(ierr);
    if (kspreason < 0) {
      if (++snes->numLinearSolveFailures >= snes->maxLinearSolveFailures) {
        snes->reason = SNES_DIVERGED_LINEAR_SOLVE;
        PetscFunctionReturn(0);
      }
    }
    ierr = KSPGetIterationNumber(snes->ksp,&lits);CHKERRQ(ierr);

    if (neP->precheckstep) {
      PetscTruth changed_y = PETSC_FALSE;
      ierr = (*neP->precheckstep)(snes,X,Y,neP->precheck,&changed_y);CHKERRQ(ierr);
    }

    if (PetscLogPrintInfo){
      ierr = SNESLSCheckResidual_Private(snes->jacobian,F,Y,G,W);CHKERRQ(ierr);
    }

    /* should check what happened to the linear solve? */
    snes->linear_its += lits;
    ierr = PetscInfo2(snes,"iter=%D, linear solve iterations=%D\n",snes->iter,lits);CHKERRQ(ierr);

    /* Compute a (scaled) negative update in the line search routine: 
         Y <- X - lambda*Y 
       and evaluate G = function(Y) (depends on the line search). 
    */
    ierr = VecCopy(Y,snes->vec_sol_update_always);CHKERRQ(ierr);
    ierr = (*neP->LineSearch)(snes,neP->lsP,X,F,G,Y,W,fnorm,&ynorm,&gnorm,&lssucceed);CHKERRQ(ierr);
    ierr = PetscInfo4(snes,"fnorm=%18.16e, gnorm=%18.16e, ynorm=%18.16e, lssucceed=%d\n",fnorm,gnorm,ynorm,(int)lssucceed);CHKERRQ(ierr);
    TMP = F; F = G; snes->vec_func_always = F; G = TMP;
    TMP = X; X = W; snes->vec_sol_always = X;  W = TMP;
    fnorm = gnorm;
    if (snes->reason == SNES_DIVERGED_FUNCTION_COUNT) break;

    ierr = PetscObjectTakeAccess(snes);CHKERRQ(ierr);
    snes->iter = i+1;
    snes->norm = fnorm;
    ierr = PetscObjectGrantAccess(snes);CHKERRQ(ierr);
    SNESLogConvHistory(snes,fnorm,lits);
    SNESMonitor(snes,i+1,fnorm);

    if (!lssucceed) {
      PetscTruth ismin;

      if (++snes->numFailures >= snes->maxFailures) {
        snes->reason = SNES_DIVERGED_Full_FAILURE;
        ierr = SNESLSCheckLocalMin_Private(snes->jacobian,F,W,fnorm,&ismin);CHKERRQ(ierr);
        if (ismin) snes->reason = SNES_DIVERGED_LOCAL_MIN;
        break;
      }
    } 

    /* Test for convergence */
    if (snes->ops->converged) {
      ierr = VecNorm(X,NORM_2,&xnorm);CHKERRQ(ierr);	/* xnorm = || X || */
      ierr = (*snes->ops->converged)(snes,snes->iter,xnorm,ynorm,fnorm,&snes->reason,snes->cnvP);CHKERRQ(ierr);
      if (snes->reason) {
        break;
      }
    }
  }
  if (X != snes->vec_sol) {
    ierr = VecCopy(X,snes->vec_sol);CHKERRQ(ierr);
  }
  if (F != snes->vec_func) {
    ierr = VecCopy(F,snes->vec_func);CHKERRQ(ierr);
  }
  snes->vec_sol_always  = snes->vec_sol;
  snes->vec_func_always = snes->vec_func;
  if (i == maxits) {
    ierr = PetscInfo1(snes,"Maximum number of iterations has been reached: %D\n",maxits);CHKERRQ(ierr);
    snes->reason = SNES_DIVERGED_MAX_IT;
  }
  PetscFunctionReturn(0);
}
/* -------------------------------------------------------------------------- */
/*
   SNESSetUp_Full - Sets up the internal data structures for the later use
   of the SNESLS nonlinear solver.

   Input Parameter:
.  snes - the SNES context
.  x - the solution vector

   Application Interface Routine: SNESSetUp()

   Notes:
   For basic use of the SNES solvers, the user need not explicitly call
   SNESSetUp(), since these actions will automatically occur during
   the call to SNESSolve().
 */
#undef __FUNCT__  
#define __FUNCT__ "SNESSetUp_Full"
PetscErrorCode SNESSetUp_Full(SNES snes)
{
  PetscErrorCode ierr;

  PetscFunctionBegin;
  if (!snes->work) {
    snes->nwork = 4;
    ierr = VecDuplicateVecs(snes->vec_sol,snes->nwork,&snes->work);CHKERRQ(ierr);
    ierr = PetscLogObjectParents(snes,snes->nwork,snes->work);CHKERRQ(ierr);
    snes->vec_sol_update_always = snes->work[3];
  }
  PetscFunctionReturn(0);
}
/* -------------------------------------------------------------------------- */
/*
   SNESDestroy_Full - Destroys the private SNES_Full context that was created
   with SNESCreate_Full().

   Input Parameter:
.  snes - the SNES context

   Application Interface Routine: SNESDestroy()
 */
#undef __FUNCT__  
#define __FUNCT__ "SNESDestroy_Full"
PetscErrorCode SNESDestroy_Full(SNES snes)
{
  PetscErrorCode ierr;

  PetscFunctionBegin;
  if (snes->nwork) {
    ierr = VecDestroyVecs(snes->work,snes->nwork);CHKERRQ(ierr);
  }
  ierr = PetscFree(snes->data);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
/* -------------------------------------------------------------------------- */
/*
   SNESView_Full - Prints info from the SNESLS data structure.

   Input Parameters:
.  SNES - the SNES context
.  viewer - visualization context

   Application Interface Routine: SNESView()
*/
#undef __FUNCT__  
#define __FUNCT__ "SNESView_Full"
static PetscErrorCode SNESView_Full(SNES snes,PetscViewer viewer)
{
  SNES_Full        *ls = (SNES_Full *)snes->data;
  const char     *cstr;
  PetscErrorCode ierr;
  PetscTruth     iascii;

  PetscFunctionBegin;
  ierr = PetscTypeCompare((PetscObject)viewer,PETSC_VIEWER_ASCII,&iascii);CHKERRQ(ierr);
  if (iascii) {
    if (ls->LineSearch == SNESLineSearchNo)             cstr = "SNESLineSearchNo";
    else if (ls->LineSearch == SNESLineSearchQuadratic) cstr = "SNESLineSearchQuadratic";
    else if (ls->LineSearch == SNESLineSearchCubic)     cstr = "SNESLineSearchCubic";
    else                                                cstr = "unknown";
    ierr = PetscViewerASCIIPrintf(viewer,"  line search variant: %s\n",cstr);CHKERRQ(ierr);
    ierr = PetscViewerASCIIPrintf(viewer,"  alpha=%G, maxstep=%G, steptol=%G\n",ls->alpha,ls->maxstep,ls->steptol);CHKERRQ(ierr);
  } else {
    SETERRQ1(PETSC_ERR_SUP,"Viewer type %s not supported for SNES EQ LS",((PetscObject)viewer)->type_name);
  }
  PetscFunctionReturn(0);
}
/* -------------------------------------------------------------------------- */
/*
   SNESSetFromOptions_Full - Sets various parameters for the SNESLS method.

   Input Parameter:
.  snes - the SNES context

   Application Interface Routine: SNESSetFromOptions()
*/
#undef __FUNCT__  
#define __FUNCT__ "SNESSetFromOptions_Full"
static PetscErrorCode SNESSetFromOptions_Full(SNES snes)
{
  SNES_Full        *ls = (SNES_Full *)snes->data;
  const char     *lses[] = {"basic","basicnonorms","quadratic","cubic"};
  PetscErrorCode ierr;
  PetscInt       indx;
  PetscTruth     flg;

  PetscFunctionBegin;
  ierr = PetscOptionsHead("SNES Line search options");CHKERRQ(ierr);
    ierr = PetscOptionsReal("-snes_ls_alpha","Function norm must decrease by","None",ls->alpha,&ls->alpha,0);CHKERRQ(ierr);
    ierr = PetscOptionsReal("-snes_ls_maxstep","Step must be less than","None",ls->maxstep,&ls->maxstep,0);CHKERRQ(ierr);
    ierr = PetscOptionsReal("-snes_ls_steptol","Step must be greater than","None",ls->steptol,&ls->steptol,0);CHKERRQ(ierr);

    ierr = PetscOptionsEList("-snes_ls","Line search used","SNESLineSearchSet",lses,4,"cubic",&indx,&flg);CHKERRQ(ierr);
    if (flg) {
      switch (indx) {
      case 0:
        ierr = SNESLineSearchSet(snes,SNESLineSearchNo,PETSC_NULL);CHKERRQ(ierr);
        break;
      case 1:
        ierr = SNESLineSearchSet(snes,SNESLineSearchNoNorms,PETSC_NULL);CHKERRQ(ierr);
        break;
      case 2:
        ierr = SNESLineSearchSet(snes,SNESLineSearchQuadratic,PETSC_NULL);CHKERRQ(ierr);
        break;
      case 3:
        ierr = SNESLineSearchSet(snes,SNESLineSearchCubic,PETSC_NULL);CHKERRQ(ierr);
        break;
      }
    }
  ierr = PetscOptionsTail();CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
/* -------------------------------------------------------------------------- */
/*MC
      SNESLS - Newton based nonlinear solver that uses a line search

   Options Database:
+   -snes_ls [cubic,quadratic,basic,basicnonorms] - Selects line search
.   -snes_ls_alpha <alpha> - Sets alpha
.   -snes_ls_maxstep <max> - Sets maxstep
-   -snes_ls_steptol <steptol> - Sets steptol, this is the minimum step size that the line search code
                   will accept; min p[i]/x[i] < steptol. The -snes_stol <stol> is the minimum step length
                   the default convergence test will use and is based on 2-norm(p) < stol*2-norm(x)

    Notes: This is the default nonlinear solver in SNES

   Level: beginner

.seealso:  SNESCreate(), SNES, SNESSetType(), SNESTR, SNESLineSearchSet(), 
           SNESLineSearchSetPostCheck(), SNESLineSearchNo(), SNESLineSearchCubic(), SNESLineSearchQuadratic(), 
          SNESLineSearchSet(), SNESLineSearchNoNorms(), SNESLineSearchSetPreCheck()

M*/
EXTERN_C_BEGIN
#undef __FUNCT__  
#define __FUNCT__ "SNESCreate_Full"
PetscErrorCode PETSCSNES_DLLEXPORT SNESCreate_Full(SNES snes)
{
  PetscErrorCode ierr;
  SNES_Full        *neP;

  PetscFunctionBegin;
  snes->ops->setup	     = SNESSetUp_Full;
  snes->ops->solve	     = SNESSolve_Full;
  snes->ops->destroy	     = SNESDestroy_Full;
  snes->ops->converged	     = SNESConverged_Full;
  snes->ops->setfromoptions  = SNESSetFromOptions_Full;
  snes->ops->view            = SNESView_Full;
  snes->nwork                = 0;
  snes->work                 = 0;

  ierr                  = PetscNew(SNES_Full,&neP);CHKERRQ(ierr);
  ierr = PetscLogObjectMemory(snes,sizeof(SNES_Full));CHKERRQ(ierr);
  snes->data    	= (void*)neP;
  neP->alpha		= 1.e-4;
  neP->maxstep		= 1.e8;
  neP->steptol		= 1.e-12;
  neP->LineSearch       = SNESLineSearchCubic;
  neP->lsP              = PETSC_NULL;
  neP->postcheckstep    = PETSC_NULL;
  neP->postcheck        = PETSC_NULL;
  neP->precheckstep     = PETSC_NULL;
  neP->precheck         = PETSC_NULL;

  PetscFunctionReturn(0);
}
EXTERN_C_END



