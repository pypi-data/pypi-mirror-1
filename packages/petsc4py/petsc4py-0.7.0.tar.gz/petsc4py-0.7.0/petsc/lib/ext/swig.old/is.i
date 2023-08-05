/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT)


PetscErrorCode 
ISCreateGeneral(MPI_Comm, 
		PetscInt, const PetscInt[], 
		IS* CREATE);

PetscErrorCode 
ISCreateBlock(MPI_Comm, 
	      PetscInt, PetscInt, const PetscInt[], 
	      IS* CREATE);

PetscErrorCode 
ISCreateStride(MPI_Comm, 
	       PetscInt, PetscInt, PetscInt, 
	       IS* CREATE);

%clear (PetscInt, const PetscInt[]);

%ignore ISCreateGeneral;
%ignore ISCreateBlock;
%ignore ISCreateStride;

%ignore ISCreateGeneralWithArray;

/* ---------------------------------------------------------------- */

#if 0
%wrapper %{
static PetscErrorCode 
ISGetType(IS iset, const char* type[])
{
  static char *ISTypes[] = {"general", "stride", "block"};
  PetscFunctionBegin;
  PetscValidHeaderSpecific(iset,IS_COOKIE,1);
  switch(((PetscObject)iset)->type) {
  case IS_GENERAL: *type = ISTypes[0]; break;
  case IS_STRIDE : *type = ISTypes[1]; break;
  case IS_BLOCK:   *type = ISTypes[2]; break;
  default:         *type = NULL;       break; 
  }
  PetscFunctionReturn(0);
}
%}

static PetscErrorCode ISGetType(IS, const char*[]);
#endif

/* ---------------------------------------------------------------- */


PetscErrorCode ISDuplicate(IS, IS* NEWOBJ);
PetscErrorCode ISInvertPermutation(IS, PetscInt, IS* NEWOBJ);

PetscErrorCode ISDifference(IS, IS, IS* NEWOBJ);
PetscErrorCode ISSum(IS* INOUT, IS);
PetscErrorCode ISExpand(IS, IS, IS* NEWOBJ);

PetscErrorCode ISAllGather(IS, IS* NEWOBJ);


%ignore ISDuplicate;
%ignore ISInvertPermutation;
%ignore ISDifference;
%ignore ISSum;
%ignore ISExpand;
%ignore ISAllGather;

/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt n, PetscInt indices[],
	   ARRAY_OUTPUT, PyPetsc_INT);

PETSC_OVERRIDE(
PetscErrorCode,
ISGetIndices, (IS iset, PetscInt n, PetscInt indices[]),
{
  PetscErrorCode ierr;
  PetscInt lsize;
  PetscInt* a;

  PetscFunctionBegin;
  PetscValidHeaderSpecific(iset,IS_COOKIE,1);
  PetscValidIntPointer(indices,2);
  ierr = ISGetLocalSize(iset,&lsize);CHKERRQ(ierr);
  n = PetscMin(lsize,n);
  ierr = ISGetIndices(iset,&a);CHKERRQ(ierr);
  ierr = PetscMemcpy(indices,a,n*sizeof(PetscInt));CHKERRQ(ierr);
  ierr = ISRestoreIndices(iset,&a);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt n, PetscInt indices[]);

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore ISGetIndices;
%ignore ISRestoreIndices;

%ignore ISBlockGetIndices;
%ignore ISBlockRestoreIndices;

%ignore ISColoringType;
%ignore MPIU_COLORING_VALUE;
%ignore IS_COLORING_MAX;
%ignore ISAllGatherColors;

%rename(iset) _p_ISColoring::is;
%rename(iset) _n_ISColoring::is;
%ignore _p_ISColoring;
%ignore _n_ISColoring;
%ignore ISColoringCreate;
%ignore ISColoringDestroy;
%ignore ISColoringView;
%ignore ISColoringGetIS;
%ignore ISColoringRestoreIS;

%ignore ISPartitioningToNumbering;
%ignore ISPartitioningCount;

%ignore ISCompressIndicesGeneral;
%ignore ISCompressIndicesSorted;
%ignore ISExpandIndicesGeneral;

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
