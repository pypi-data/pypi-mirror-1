/* $Id$ */

/* ---------------------------------------------------------------- */

%apply (PetscInt, PetscObject INPUT[])  
       { (PetscInt n, const Vec vecs[]) };
%typemap(check) (PetscInt n, const Vec vecs[]) {
  int        i;
  PetscTruth valid;
  for (i=0; i<$1; i++) {
    VecValid($2[i],&valid);
    if (!valid)
      PETSC_seterr(PETSC_ERR_ARG_WRONG,
		   "object in `vecs` is not a valid vector");
  }
}

PetscErrorCode
MatNullSpaceCreate(MPI_Comm,  PetscTruth, 
		   PetscInt n, const Vec vecs[],
		   MatNullSpace* CREATE);

%clear (PetscInt n, const Vec vecs[]);

/* ---------------------------------------------------------------- */

%apply Vec OBJ_OR_NONE { Vec out };

PETSC_OVERRIDE(
PetscErrorCode,
MatNullSpaceRemove,
(MatNullSpace nullsp, Vec vec, Vec out), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(nullsp,MAT_NULLSPACE_COOKIE,1);
  PetscValidHeaderSpecific(vec,VEC_COOKIE,2);
  if (out) {
    Vec v;
    PetscValidHeaderSpecific(out,VEC_COOKIE,3);
    ierr = MatNullSpaceRemove(nullsp,vec,&v); CHKERRQ(ierr);
    ierr = VecCopy(v,out); CHKERRQ(ierr);
  } else {
    ierr = MatNullSpaceRemove(nullsp,vec,PETSC_NULL); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

%clear Vec out;

/* ---------------------------------------------------------------- */

%ignore MatNullSpaceSetFunction;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
