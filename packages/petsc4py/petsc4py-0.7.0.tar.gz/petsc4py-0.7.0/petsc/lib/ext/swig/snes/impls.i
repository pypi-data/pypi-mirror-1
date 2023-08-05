%inline %{
#define LS_BASIC      "basic"
#define LS_NO_NORMS   "basicnonorms"
#define LS_QUADRATIC  "quadratic"
#define LS_CUBIC      "cubic"
%}

%wrapper %{
static
PetscErrorCode SNESLineSearchSetType(SNES snes, const char ls[]) {
  PetscErrorCode ierr;
  PetscTruth     same;
  PetscInt       ils=-1;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(snes,SNES_COOKIE,1);
  PetscValidCharPointer(ls,2);
  /*PetscValidType(snes,1);*/
  ierr = PetscTypeCompare((PetscObject)snes,SNESLS,&same);CHKERRQ(ierr);
  if (!same) { PetscFunctionReturn(0); }
  ierr = PetscStrcmp(ls,LS_BASIC,&same);CHKERRQ(ierr);
  if (same) { ils = 0; goto finally; }
  ierr = PetscStrcmp(ls,LS_NO_NORMS,&same);CHKERRQ(ierr);
  if (same) { ils = 1; goto finally; }
  ierr = PetscStrcmp(ls,LS_QUADRATIC,&same);CHKERRQ(ierr);
  if (same) { ils = 2; goto finally; }
  ierr = PetscStrcmp(ls,LS_CUBIC,&same);CHKERRQ(ierr);
  if (same) { ils = 3; goto finally; }
 finally:
  switch (ils) {
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
  PetscFunctionReturn(0);
}
%}

PetscErrorCode SNESLineSearchSetType(SNES,const char*);
PetscErrorCode SNESLineSearchSetParams(SNES,PetscReal,PetscReal,PetscReal);
PetscErrorCode SNESLineSearchGetParams(SNES snes,PetscReal*,PetscReal*,PetscReal*);

PetscErrorCode SNESSetTrustRegionTolerance(SNES,PetscReal);

/*
 * Local Variables:
 * mode: C
 * End:
 */
