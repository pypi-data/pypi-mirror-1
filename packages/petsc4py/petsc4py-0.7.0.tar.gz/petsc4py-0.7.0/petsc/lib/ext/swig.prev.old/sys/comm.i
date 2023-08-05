/* $Id$ */

/* ---------------------------------------------------------------- */

%wrapper %{
#undef  __FUNCT__  
#define __FUNCT__ "PetscGetCommNull"
PetscErrorCode PetscGetCommNull(MPI_Comm* comm)
{
  PetscFunctionBegin;
  *comm = MPI_COMM_NULL;
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PetscGetCommSelf"
PetscErrorCode PetscGetCommSelf(MPI_Comm* comm) 
{
  PetscFunctionBegin;
  *comm = PETSC_COMM_SELF;
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PetscGetCommWorld"
PetscErrorCode PetscGetCommWorld(MPI_Comm* comm)
{
  PetscFunctionBegin;
  *comm = PETSC_COMM_WORLD;
  PetscFunctionReturn(0);
}
%}

PetscErrorCode PetscGetCommNull(MPI_Comm* comm);
PetscErrorCode PetscGetCommSelf(MPI_Comm* comm); 
PetscErrorCode PetscGetCommWorld(MPI_Comm* comm);

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
PetscCommDuplicate,
(MPI_Comm comm, MPI_Comm* newcomm),{
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscCommDuplicate(comm, newcomm, NULL);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%apply MPI_Comm* INPUT { MPI_Comm* comm }
PETSC_OVERRIDE(
PetscErrorCode,
PetscCommDestroy,
(MPI_Comm* comm),{
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = PetscCommDestroy(comm);CHKERRQ(ierr);
  *comm = MPI_COMM_NULL;
  PetscFunctionReturn(0);
})
%clear MPI_Comm* comm;

/* ---------------------------------------------------------------- */


%wrapper %{
#undef  __FUNCT__  
#define __FUNCT__ "PetscCommSetComm"
PetscErrorCode PetscCommSetComm(MPI_Comm* self, MPI_Comm comm)
{
  PetscFunctionBegin;
  *self = comm;
  PetscFunctionReturn(0);
}
#undef  __FUNCT__  
#define __FUNCT__ "PetscCommGetRank"
PetscErrorCode PetscCommGetRank(MPI_Comm comm, int* rank) 
{
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MPI_Comm_rank(comm, rank);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PetscCommGetSize"
PetscErrorCode PetscCommGetSize(MPI_Comm comm, int* size)
{
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MPI_Comm_size(comm, size);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#undef  __FUNCT__  
#define __FUNCT__ "PetscCommBarrier"
PetscErrorCode PetscCommBarrier(MPI_Comm comm) 
{
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MPI_Barrier(comm); CHKERRQ(ierr);
  PetscFunctionReturn(0);
}
%}

%apply MPI_Comm* INPUT { MPI_Comm* self }
%typemap(check) MPI_Comm* self "";
%typemap(check) MPI_Comm  comm "";
PetscErrorCode PetscCommSetComm(MPI_Comm* self, MPI_Comm comm);
%clear MPI_Comm* self;
%clear MPI_Comm  comm;
PetscErrorCode PetscCommGetRank(MPI_Comm comm, int* rank); 
PetscErrorCode PetscCommGetSize(MPI_Comm comm, int* size); 
PetscErrorCode PetscCommBarrier(MPI_Comm comm);

/* ---------------------------------------------------------------- */

%wrapper %{
#define PetscGlobalMin(local,result,comm) \
        PetscGlobalMin(&local,result,comm)
#define PetscGlobalMax(local,result,comm) \
        PetscGlobalMax(&local,result,comm)
#define PetscGlobalSum(local,result,comm) \
        PetscGlobalSum(&local,result,comm)
%}

PetscErrorCode
PetscGlobalMin(PetscReal local, PetscReal* result, MPI_Comm comm);
PetscErrorCode
PetscGlobalMax(PetscReal local, PetscReal* result, MPI_Comm comm);
PetscErrorCode
PetscGlobalSum(PetscScalar local, PetscScalar* result, MPI_Comm comm);

%wrapper %{
#undef PetscGlobalMin
#undef PetscGlobalMax
#undef PetscGlobalSum
%}

%ignore PetscGlobalMin;
%ignore PetscGlobalMax;
%ignore PetscGlobalSum;

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore PETSC_COMM_SELF;
%ignore PETSC_COMM_WORLD;
%ignore PetscGlobalRank;
%ignore PetscGlobalSize;
%ignore PetscCommGetNewTag;
%ignore MPICCommToFortranComm;
%ignore MPIFortranCommToCComm;

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
