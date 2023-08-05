/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode VecScatterCreate(Vec, IS OPTIONAL, 
				Vec, IS OPTIONAL,
				VecScatter* CREATE);

/* ---------------------------------------------------------------- */

PetscErrorCode VecScatterCopy(VecScatter, VecScatter* NEWOBJ);
PetscErrorCode VecScatterCreateToAll(Vec, VecScatter* NEWOBJ, Vec* NEWOBJ);
PetscErrorCode VecScatterCreateToZero(Vec, VecScatter* NEWOBJ, Vec* NEWOBJ);

/* ---------------------------------------------------------------- */

PetscErrorCode VecScatterBegin(Vec x,Vec y,InsertMode,ScatterMode,VecScatter);
PetscErrorCode VecScatterEnd(Vec x,Vec y,InsertMode,ScatterMode,VecScatter);

/* ---------------------------------------------------------------- */



/*
 * Local Variables:
 * mode: C
 * End:
 */
