#define PETSCKSP_DLL

#include "src/ksp/pc/impls/nsi/nsi.h"      /*I "petscpc.h" I*/

/* -------------------------------------------------------------------------- */

/*
  PCSetFromOptions_NSI - 

   Input Parameter:
.  pc - the preconditioner context

  Application Interface Routine: PCSetFromOptions()
*/

#undef __FUNCT__  
#define __FUNCT__ "PCSetFromOptions_NSI"
static PetscErrorCode PCSetFromOptions_NSI(PC pc)
{
  PC_NSI         *nsi = (PC_NSI*)pc->data;
  PetscTruth     flg;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  ierr = PetscOptionsHead("NSI options");CHKERRQ(ierr);

  ierr = PetscOptionsTail();CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

/* -------------------------------------------------------------------------- */

/* forward declarations */

EXTERN_C_BEGIN
PetscErrorCode PETSCKSP_DLLEXPORT PCCreate_NSI(PC);
EXTERN_C_END

static PetscErrorCode PCDestroy_NSI(PC);

#undef __FUNCT__  
#define __FUNCT__ "PCSetUp_NSI"
/*
   PCSetUp_NSI - Prepares for the use of the NSI preconditioner
                   by setting data structures and options.

   Input Parameter:
.  pc - the preconditioner context

   Application Interface Routine: PCSetUp()

   Notes:
   The interface routine PCSetUp() is not usually called directly by
   the user, but instead is called by PCApply() if necessary.
*/
static PetscErrorCode PCSetUp_NSI(PC pc)
{
  PC_NSI         *nsi=(PC_NSI*)(pc->data);
  PetscErrorCode ierr;
  PetscFunctionBegin;

  
  if (!pc->pmat) SETERRQ(PETSC_ERR_ORDER,"You must call KSPSetOperators() or PCSetOperators() before this call");
  
  if (!pc->setupcalled) {
    
    ierr = 0; CHKERRQ(ierr);
    
  } else if (pc->flag == SAME_NONZERO_PATTERN) {
    
    ierr = 0; CHKERRQ(ierr);

  } else {

    ierr = 0; CHKERRQ(ierr);

  }

  PetscFunctionReturn(0);
}

/* -------------------------------------------------------------------------- */

/*
   PCApply_NSI - Applies the NSI preconditioner to a vector.

   Input Parameters:
.  pc - the preconditioner context
.  r - input vector

   Output Parameter:
.  z - output vector

   Application Interface Routine: PCApply()
 */
#undef __FUNCT__  
#define __FUNCT__ "PCApply_NSI"
static PetscErrorCode PCApply_NSI(PC pc,Vec r,Vec z)
{
  PC_NSI         *nsi = (PC_NSI*)pc->data;
  PetscInt       i;
  PetscErrorCode ierr;
  PetscFunctionBegin;

  ierr = VecCopy(r,z);CHKERRQ(ierr);
  PetscFunctionReturn(0);
  

  PetscFunctionReturn(0);
}

/* -------------------------------------------------------------------------- */

/*
  PCView_NSI - 

   Input Parameter:
.  pc - the preconditioner context
.  viewer - the viewer context

  Application Interface Routine: PCView()
*/
#undef __FUNCT__  
#define __FUNCT__ "PCView_NSI"
static PetscErrorCode PCView_NSI(PC pc,PetscViewer viewer)
{
  PC_NSI       *nsi = (PC_NSI*)pc->data;
  PetscTruth   iascii;

  PetscErrorCode ierr;
  PetscFunctionBegin;

  ierr = PetscTypeCompare((PetscObject)viewer,PETSC_VIEWER_ASCII,&iascii);CHKERRQ(ierr);
  if (!iascii) {
    SETERRQ1(PETSC_ERR_SUP,"Viewer type %s not supported for PC NSI",((PetscObject)viewer)->type_name);
    PetscFunctionReturn(0);
  }

  PetscFunctionReturn(0);
}

/* -------------------------------------------------------------------------- */

PETSC_EXTERN_CXX_BEGIN
EXTERN PetscErrorCode PETSCKSP_DLLEXPORT PCNSIGetSubKSP(PC,PetscInt*,KSP**);
PETSC_EXTERN_CXX_END

EXTERN_C_BEGIN
#undef __FUNCT__  
#define __FUNCT__ "PCNSIGetSubKSP_NSI"
PetscErrorCode PETSCKSP_DLLEXPORT PCNSIGetSubKSP_NSI(PC pc,PetscInt *n,KSP **ksp)
{
  PC_NSI       *nsi = (PC_NSI*)pc->data;
  PetscFunctionBegin;
  if (pc->setupcalled) {
    if (n)   *n   = nsi->nd+1;
    if (ksp) *ksp = nsi->ksp;
  } else {
    if (n)   *n   = 0;
    if (ksp) *ksp = PETSC_NULL;
    SETERRQ(PETSC_ERR_ORDER,"Need to call PCSetUP() on PC (or KSPSetUp() on the outer KSP object) before calling this");
  }
  PetscFunctionReturn(0);
}
EXTERN_C_END

#undef __FUNCT__  
#define __FUNCT__ "PCNSIGetSubKSP"
/*@C
   PCNSIGetSubKSP - 

   Input Parameter:
.  pc - the preconditioner context

   Output Parameters:
.  n - the number of KSP contexts
-  ksp - the array of KSP contexts

   Note:  
   After PCNSIGetSubKSP() the array of KSPes is not to be freed

   You must call KSPSetUp() before calling PCNSIGetSubKSP().

   Level: advanced

.keywords: PC, KSP

@*/
PetscErrorCode PETSCKSP_DLLEXPORT PCNSIGetSubKSP(PC pc,PetscInt *n,KSP *ksp[])
{
  PetscErrorCode ierr,(*f)(PC,PetscInt*,KSP **);
  PetscFunctionBegin;
  PetscValidHeaderSpecific(pc,PC_COOKIE,1);
  ierr = PetscObjectQueryFunction((PetscObject)pc,"PCNSIGetSubKSP_C",(void (**)(void))&f);CHKERRQ(ierr);
  if (f) {
    ierr = (*f)(pc,n,ksp);CHKERRQ(ierr);
  } else {
    SETERRQ(PETSC_ERR_ARG_WRONG,"Cannot get subsolvers for this type of PC");
  }
 PetscFunctionReturn(0);
}

/* -------------------------------------------------------------------------- */

PETSC_EXTERN_CXX_BEGIN
EXTERN PetscErrorCode PETSCKSP_DLLEXPORT PCNSISetIndices(PC,PetscInt,IS[],IS);
PETSC_EXTERN_CXX_END

EXTERN_C_BEGIN
#undef __FUNCT__  
#define __FUNCT__ "PCNSIGetSubKSP_NSI"
PetscErrorCode PETSCKSP_DLLEXPORT PCNSISetIndices_NSI(PC pc,PetscInt nd,IS u[],IS p)
{
  PC_NSI         *nsi = (PC_NSI*)pc->data;
  PetscInt       i;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (nd < 1 || nd > 3) SETERRQ1(1,"invalid number of dimensions: %D",nd);
  for (i=0; i<nd; i++)
    PetscValidHeaderSpecific(u[i],IS_COOKIE,3);
  PetscValidHeaderSpecific(p,IS_COOKIE,4);
  for (i=0; i<(nsi->nd+1); i++) {
    if (nsi->is[i]) { ierr = ISDestroy(nsi->is[i]);CHKERRQ(ierr); }
    nsi->is[i] = 0;
  }
  nsi->nd = nd;
  for (i=0; i<nsi->nd; i++) nsi->is[i] = u[i];
  nsi->is[i] = p;
  PetscFunctionReturn(0);
}
EXTERN_C_END

#undef __FUNCT__  
#define __FUNCT__ "PCNSISetIndices"
PetscErrorCode PETSCKSP_DLLEXPORT PCNSISetIndices(PC pc,PetscInt nd,IS u[],IS p)
{
  PetscErrorCode ierr,(*f)(PC,PetscInt,IS*,IS);
  PetscFunctionBegin;
  PetscValidHeaderSpecific(pc,PC_COOKIE,1);
  ierr = PetscObjectQueryFunction((PetscObject)pc,"PCNSISetIndices_C",(void (**)(void))&f);CHKERRQ(ierr);
  if (f) {
    ierr = (*f)(pc,nd,u,p);CHKERRQ(ierr);
  }
 PetscFunctionReturn(0);
}

/* -------------------------------------------------------------------------- */


/*
   PCDestroy_NSI - Destroys the private context for the NSI preconditioner
   that was created with PCCreate_NSI().

   Input Parameter:
.  pc - the preconditioner context

   Application Interface Routine: PCDestroy()
*/
#undef __FUNCT__  
#define __FUNCT__ "PCDestroy_NSI"
static PetscErrorCode PCDestroy_NSI(PC pc)
{
  PC_NSI         *nsi = (PC_NSI*)pc->data;
  PetscInt       i;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  /* Free internal objects */
  for (i=0; i<(nsi->nd+1); i++) {
    if (nsi->is[i])      {ierr = ISDestroy(nsi->is[i]);CHKERRQ(ierr);}
    if (nsi->vec1[i])    {ierr = VecDestroy(nsi->vec1[i]);CHKERRQ(ierr);}
    if (nsi->vec2[i])    {ierr = VecDestroy(nsi->vec1[i]);CHKERRQ(ierr);}
    if (nsi->scatter[i]) {ierr = VecScatterDestroy(nsi->scatter[i]);CHKERRQ(ierr);}
    if (nsi->ksp[i])     {ierr = KSPDestroy(nsi->ksp[i]);CHKERRQ(ierr);}

  }
  for (i=0; i<nsi->nd; i++) {
    if (nsi->F[i]) {ierr = MatDestroy(nsi->F[i]);CHKERRQ(ierr);}
  }
  if (nsi->B1) {ierr = MatDestroy(nsi->B1);CHKERRQ(ierr);}
  if (nsi->B2) {ierr = MatDestroy(nsi->B2);CHKERRQ(ierr);}
  if (nsi->C)  {ierr = MatDestroy(nsi->C);CHKERRQ(ierr);}

  /* Free the private data structure */
  ierr = PetscFree(nsi);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

/* -------------------------------------------------------------------------- */

/*MC
   PCNSI - Incompressible Navier-Stokes preconditioner.

   Options Database Keys:
+  -pc_nsi_xxx - XXX explain this
.  -pc_nsi_xxx - XXX explain this
.  -pc_nsi_xxx - XXX explain this
-  -sub_[u,p]_[ksp,pc]_ - Options for subsolvers
   Level: intermediate

   Concepts: physics based preconditioners

   Contributed by Lisandro Dalcin <dalcinl at gmail dot com>

.seealso:  PCCreate(), PCSetType(), PCType (for list of available types), PC
M*/
EXTERN_C_BEGIN
#undef __FUNCT__  
#define __FUNCT__ "PCCreate_NSI"
PetscErrorCode PETSCKSP_DLLEXPORT PCCreate_NSI(PC pc)
{
  PC_NSI       *nsi;
  PetscErrorCode ierr;
  PetscFunctionBegin;

  ierr = PetscNew(PC_NSI,&nsi);CHKERRQ(ierr);
  ierr = PetscLogObjectMemory(pc,sizeof(PC_NSI));CHKERRQ(ierr);

  pc->data  = (void*)nsi;

  pc->ops->setfromoptions      = PCSetFromOptions_NSI;
  pc->ops->setup               = PCSetUp_NSI;
  pc->ops->apply               = PCApply_NSI;
  pc->ops->view                = PCView_NSI;
  pc->ops->destroy             = PCDestroy_NSI;

  pc->ops->applytranspose      = 0;
  pc->ops->presolve            = 0;
  pc->ops->postsolve           = 0;
  pc->ops->applyrichardson     = 0;
  pc->ops->applysymmetricleft  = 0;
  pc->ops->applysymmetricright = 0;

  ierr = PetscObjectComposeFunctionDynamic((PetscObject)pc,"PCNSIGetSubKSP_C","PCNSIGetSubKSP_NSI",
					   PCNSIGetSubKSP_NSI);CHKERRQ(ierr);

  PetscFunctionReturn(0);
}
EXTERN_C_END

/* -------------------------------------------------------------------------- */
