/* $Id$ */

/* ---------------------------------------------------------------- */

%define LGMAP_RENAME(FUN)
%rename(LGMapping##FUN) ISLocalToGlobalMapping##FUN;
%enddef

LGMAP_RENAME(Create);
LGMAP_RENAME(CreateIS);
LGMAP_RENAME(Block);
LGMAP_RENAME(Apply);
LGMAP_RENAME(ApplyIS);
LGMAP_RENAME(GetSize);
LGMAP_RENAME(GetInfo);

/* ---------------------------------------------------------------- */


%apply ISLocalToGlobalMapping* CREATE 
       { ISLocalToGlobalMapping* mapping };

ARRAY_FLAT(PetscInt n, const PetscInt indices[], 
	   ARRAY_INPUT, PyPetsc_INT)

PETSC_OVERRIDE(
PetscErrorCode,
LGMappingCreate,(MPI_Comm comm,
		 PetscInt n, const PetscInt indices[],
		 ISLocalToGlobalMapping* mapping), {

  PetscInt       *in = PETSC_NULL;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  PetscValidPointer(mapping,4);
  if (n) {
    PetscValidIntPointer(indices,3);
    ierr = PetscMalloc(n*sizeof(PetscInt),&in);CHKERRQ(ierr);
    ierr = PetscMemcpy(in,indices,n*sizeof(PetscInt));CHKERRQ(ierr);
  }
  ierr = ISLocalToGlobalMappingCreateNC(comm,n,in,mapping);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt n, const PetscInt indices[]);
%clear ISLocalToGlobalMapping* mapping;

PetscErrorCode ISLocalToGlobalMappingCreateIS(IS,ISLocalToGlobalMapping* CREATE);

PetscErrorCode ISLocalToGlobalMappingView(ISLocalToGlobalMapping,PetscViewer);
PetscErrorCode ISLocalToGlobalMappingDestroy(ISLocalToGlobalMapping);

PetscErrorCode ISLocalToGlobalMappingApplyIS(ISLocalToGlobalMapping,IS,IS* NEWOBJ);

ARRAY_PAIR(PetscInt N, const PetscInt in[], PetscInt out[],
	   ARRAY_INPUT,  PyPetsc_INT,
	   ARRAY_OUTPUT, PyPetsc_INT)
ARRAY_PAIR_CHECK_SIZE(PetscInt N, 
		      const PetscInt in[],
		      PetscInt out[])

PETSC_OVERRIDE(
PetscErrorCode,
LGMappingApply,(ISLocalToGlobalMapping mapping,
		PetscInt N, const PetscInt in[], PetscInt out[]), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = ISLocalToGlobalMappingApply(mapping,N,in,out); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt N,const PetscInt in[],PetscInt out[]);


ARRAY_FLAT(PetscInt n, const PetscInt idx[],
	   ARRAY_INPUT, PyPetsc_INT)
ARRAY_1D_NEW(PetscInt *nout, PetscInt** idxout,
	     PyPetsc_INT)
ARRAY_1D_FREEARG(PetscInt *nout, PetscInt** idxout,
		 PetscFree)

PETSC_OVERRIDE(
PetscErrorCode,
LGMappingApplyInverse,(ISLocalToGlobalMapping mapping,
		       ISGlobalToLocalMappingType type,
		       PetscInt n, const PetscInt idx[], 
		       PetscInt *nout, PetscInt** idxout), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  *idxout = PETSC_NULL;
  ierr = ISGlobalToLocalMappingApply(mapping, type, 
				     n,    idx, 
				     nout, *idxout);CHKERRQ(ierr);
  if (*nout) {
    ierr = PetscMalloc((*nout)*sizeof(PetscInt), idxout); CHKERRQ(ierr);
  }
  ierr = ISGlobalToLocalMappingApply(mapping, type, 
				     n,    idx,
				     nout, *idxout);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt n, const PetscInt idx[]);
%clear (PetscInt nout, PetscInt** idxout);


PetscErrorCode ISLocalToGlobalMappingGetSize(ISLocalToGlobalMapping,PetscInt*);

%typemap(in, numinputs = 0) 
(PetscInt*, PetscInt*[], PetscInt*[], PetscInt**[])
(PetscInt nproc, PetscInt *procs, PetscInt *nind, PetscInt **indices)
{ 
  nproc = 0;   procs = NULL; nind = NULL; indices = NULL;
  $1 = &nproc; $2 = &procs;  $3 = &nind;  $4 = &indices;
}
%typemap(argout)
(PetscInt*, PetscInt*[], PetscInt*[], PetscInt**[]) {
  PetscInt i;
  PyObject* o;
  o = ARRAY_NEW(*$2,PyPetsc_INT,1,*$1);
  if (o == NULL) goto fail_arg;
  %append_output(o);
  o = PyList_New(*$1);
  if (o == NULL) goto fail_arg;
  for (i=0; i<*$1; i++) {
    PyObject* p = ARRAY_NEW((*$4)[i], PyPetsc_INT,1,(*$3)[i]);
    if (p == NULL) goto fail_arg;
    PyList_SetItem(o,i,p);
    if (PyErr_Occurred()) goto fail_arg;
  }
  %append_output(o);
 fail_arg:
  if (PyErr_Occurred()) {
    Py_XDECREF($result); $result = NULL;
    %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  }
}
%typemap(freearg)
(PetscInt*, PetscInt*[], PetscInt*[], PetscInt**[])
{ ISLocalToGlobalMappingRestoreInfo(arg1,$1,$2,$3,$4); };

PetscErrorCode ISLocalToGlobalMappingGetInfo(ISLocalToGlobalMapping,PetscInt*,PetscInt*[],PetscInt*[],PetscInt**[]);
%clear (PetscInt*, PetscInt*[], PetscInt*[], PetscInt**[]);

//PetscErrorCode ISLocalToGlobalMappingRestoreInfo(ISLocalToGlobalMapping,PetscInt*,PetscInt*[],PetscInt*[],PetscInt**[]);

PetscErrorCode ISLocalToGlobalMappingBlock(ISLocalToGlobalMapping,PetscInt,ISLocalToGlobalMapping* CREATE);


/* ---------------------------------------------------------------- */



/*
 * Local Variables:
 * mode: C
 * End:
 */
