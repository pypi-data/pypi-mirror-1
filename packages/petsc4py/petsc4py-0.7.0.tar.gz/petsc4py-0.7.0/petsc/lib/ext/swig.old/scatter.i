/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode
VecScatterCreate(Vec, IS OBJ_OR_NONE, 
		 Vec, IS OBJ_OR_NONE,
		 VecScatter* CREATE);

PetscErrorCode
VecScatterCopy(VecScatter, VecScatter* NEWOBJ);

PetscErrorCode
VecScatterCreateToAll(Vec, VecScatter* NEWOBJ, Vec* NEWOBJ);

PetscErrorCode
VecScatterCreateToZero(Vec, VecScatter* NEWOBJ, Vec* NEWOBJ);

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* Ignores                                                          */
/* ---------------------------------------------------------------- */

%ignore VEC_ScatterBarrier;
%ignore VEC_ScatterBegin;
%ignore VEC_ScatterEnd;

%ignore VecScatterRemap(VecScatter,PetscInt*,PetscInt*);

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
