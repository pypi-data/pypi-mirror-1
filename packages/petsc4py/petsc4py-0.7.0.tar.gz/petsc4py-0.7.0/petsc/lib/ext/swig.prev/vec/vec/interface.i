/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode VecCreate(MPI_Comm, Vec* CREATE);

PetscErrorCode VecCreateSeq(MPI_Comm, PetscInt, Vec* CREATE);

PetscErrorCode VecCreateMPI(MPI_Comm, PetscInt, PetscInt, Vec* CREATE);

PetscErrorCode VecCreateShared(MPI_Comm, PetscInt, PetscInt, Vec* CREATE);


ARRAY_FLAT(PetscInt nghost, const PetscInt ghosts[],
	   ARRAY_INPUT, PyPetsc_INT)
PetscErrorCode VecCreateGhost(MPI_Comm,
			      PetscInt, PetscInt, 
			      PetscInt nghost, const PetscInt ghosts[],
			      Vec* CREATE);
PetscErrorCode VecCreateGhostBlock(MPI_Comm,
				   PetscInt, PetscInt, PetscInt,
				   PetscInt nghost, const PetscInt ghosts[],
				   Vec* CREATE);
%clear (PetscInt nghost, const PetscInt ghosts[]);

PetscErrorCode VecDestroy(Vec);
PetscErrorCode VecView(Vec,PetscViewer);

PetscErrorCode VecSetType(Vec, VecType);
PetscErrorCode VecGetType(Vec, VecType *);

PetscErrorCode VecSetOptionsPrefix(Vec,const char[]);
PetscErrorCode VecAppendOptionsPrefix(Vec,const char[]);
PetscErrorCode VecGetOptionsPrefix(Vec,const char*[]);
PetscErrorCode VecSetFromOptions(Vec);
PetscErrorCode VecSetUp(Vec);

PetscErrorCode VecSetSizes(Vec,PetscInt,PetscInt);
PetscErrorCode VecGetSize(Vec,PetscInt*);
PetscErrorCode VecGetLocalSize(Vec,PetscInt*);
PetscErrorCode VecGetOwnershipRange(Vec,PetscInt*,PetscInt*);

PetscErrorCode VecSetBlockSize(Vec,PetscInt);
PetscErrorCode VecGetBlockSize(Vec,PetscInt*);


PetscErrorCode VecSetOption(Vec,VecOption);

PetscErrorCode VecDuplicate(Vec,Vec* NEWOBJ);

PetscErrorCode VecEqual(Vec,Vec,PetscTruth*);

PetscErrorCode VecGhostGetLocalForm(Vec, Vec* NEWOBJ);
PetscErrorCode VecGhostUpdateBegin(Vec,InsertMode,ScatterMode);
PetscErrorCode VecGhostUpdateEnd(Vec,InsertMode,ScatterMode);

%typemap(arginit) VecType outtype "$1 = NULL;";
%typemap(in, noblock=1) VecType outtype {
  if ($input!=Py_None) {
    $1 = PyString_AsString($input);
    if (PyErr_Occurred()) SWIG_fail;
  }
}
PetscErrorCode VecLoad(PetscViewer, VecType outtype, Vec* NEWOBJ);
%clear VecType outtype;

PetscErrorCode VecLoadIntoVector(PetscViewer viewer, Vec vec);


/* ---------------------------------------------------------------- */
PetscErrorCode VecZeroEntries(Vec);
PetscErrorCode VecConjugate(Vec);
PetscErrorCode VecNormalize(Vec,PetscReal*);
PetscErrorCode VecSum(Vec,PetscScalar*);
PetscErrorCode VecMax(Vec,PetscInt*,PetscReal*);
PetscErrorCode VecMin(Vec,PetscInt*,PetscReal*);
PetscErrorCode VecScale(Vec,PetscScalar);
PetscErrorCode VecCopy(Vec,Vec);        
PetscErrorCode VecSetRandom(Vec,PetscRandom OPTIONAL);
PetscErrorCode VecSet(Vec,PetscScalar);
PetscErrorCode VecSwap(Vec,Vec);
PetscErrorCode VecAXPY(Vec,PetscScalar,Vec);  
PetscErrorCode VecAXPBY(Vec,PetscScalar,PetscScalar,Vec);  
PetscErrorCode VecMAXPY(Vec,PetscInt,const PetscScalar[],Vec*);
PetscErrorCode VecAYPX(Vec,PetscScalar,Vec);
PetscErrorCode VecWAXPY(Vec,PetscScalar,Vec,Vec);
PetscErrorCode VecPointwiseMax(Vec,Vec,Vec);    
PetscErrorCode VecPointwiseMaxAbs(Vec,Vec,Vec);
PetscErrorCode VecPointwiseMin(Vec,Vec,Vec);
PetscErrorCode VecPointwiseMult(Vec,Vec,Vec);
PetscErrorCode VecPointwiseDivide(Vec,Vec,Vec);    
PetscErrorCode VecMaxPointwiseDivide(Vec,Vec,PetscReal*);    
PetscErrorCode VecShift(Vec,PetscScalar);
PetscErrorCode VecReciprocal(Vec);
PetscErrorCode VecPermute(Vec,IS,PetscTruth);
PetscErrorCode VecSqrt(Vec);
PetscErrorCode VecAbs(Vec);

/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT)

ARRAY_RAW(PetscScalar[],
	  ARRAY_OUTPUT, PyPetsc_SCALAR)

%typemap(check) 
     (PetscInt,const PetscInt[],const PetscScalar[])
{ ARRAY_check_size(array4, ($1)); }

PetscErrorCode VecGetValues(Vec,PetscInt,const PetscInt[],PetscScalar[]);

%clear (PetscInt, const PetscInt[]);
%clear PetscScalar[];
%clear (PetscInt, const PetscInt[], PetscScalar[]);


ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT)

ARRAY_RAW(const PetscScalar[],
	  ARRAY_INPUT, PyPetsc_SCALAR)

%typemap(check) 
     (PetscInt,const PetscInt[],const PetscScalar[])
{ ARRAY_check_size(array4, ($1)); }

PetscErrorCode VecSetValues(Vec,PetscInt,const PetscInt[],const PetscScalar[],InsertMode);
PetscErrorCode VecSetValuesLocal(Vec,PetscInt,const PetscInt[],const PetscScalar[],InsertMode);

%clear (PetscInt, const PetscInt[]);
%clear  const PetscScalar[];
%clear (PetscInt,const PetscInt[],const PetscScalar[]);


PetscErrorCode VecSetLocalToGlobalMapping(Vec,ISLocalToGlobalMapping);
PetscErrorCode VecSetLocalToGlobalMappingBlock(Vec,ISLocalToGlobalMapping);

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
VecGetValue,
(Vec vec,PetscInt i,PetscScalar* v), { 
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = VecGetValues(vec,1,&i,v);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
VecSetValue,
(Vec vec,PetscInt i,PetscScalar v,InsertMode im), {
  return VecSetValues(vec,1,&i,&v,im);
})

PETSC_OVERRIDE(
PetscErrorCode,
VecSetValueLocal,
(Vec vec,PetscInt i,PetscScalar v,InsertMode im), {
  return VecSetValuesLocal(vec,1,&i,&v,im);
})

/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT)

ARRAY_RAW(const PetscScalar[],
	  ARRAY_INPUT, PyPetsc_SCALAR)

%typemap(check) (PetscInt,const PetscInt[],const PetscScalar[]) {
  PetscInt bsize; VecGetBlockSize(arg1, &bsize);
  if (bsize ==-1) 
    PETSC_seterr(PETSC_ERR_ORDER, "block size not set");
  ARRAY_check_size(array4, $1*bsize);
}

PetscErrorCode 
VecSetValuesBlocked(Vec,
		    PetscInt, const PetscInt[],  const PetscScalar[],
		    InsertMode);

PetscErrorCode 
VecSetValuesBlockedLocal(Vec, 
			 PetscInt, const PetscInt[], const PetscScalar[],
			 InsertMode);

%clear (PetscInt, const PetscInt[]);
%clear  const PetscScalar[];
%clear (PetscInt,const PetscInt[],const PetscScalar[]);

PetscErrorCode VecAssemblyBegin(Vec);
PetscErrorCode VecAssemblyEnd(Vec);

/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt n, PetscScalar array[],
	   ARRAY_OUTPUT, PyPetsc_SCALAR)

PETSC_OVERRIDE(
PetscErrorCode,
VecGetArray,
(Vec vec, PetscInt n, PetscScalar array[]), {
  PetscErrorCode ierr;
  PetscInt lsize;
  PetscScalar* a;

  PetscFunctionBegin;
  PetscValidHeaderSpecific(vec,VEC_COOKIE,1);
  PetscValidScalarPointer(array,2);
  PetscValidType(vec,1);
  ierr = VecGetLocalSize(vec,&lsize);CHKERRQ(ierr);
  ierr = VecGetArray(vec,&a); CHKERRQ(ierr);
  n = PetscMin(lsize, n);
  ierr = PetscMemcpy(array,a,n*sizeof(PetscScalar));CHKERRQ(ierr);
  ierr = VecRestoreArray(vec,&a); CHKERRQ(ierr);
  ierr = PetscObjectStateDecrease((PetscObject)vec);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt n, PetscScalar array[]);

ARRAY_FLAT(PetscInt n, const PetscScalar array[],
	   ARRAY_INPUT, PyPetsc_SCALAR)

PETSC_OVERRIDE(
PetscErrorCode,
VecSetArray,
(Vec vec, PetscInt n, const PetscScalar array[]), {
  PetscErrorCode ierr;
  PetscInt lsize;
  PetscScalar* a;

  PetscFunctionBegin;
  PetscValidHeaderSpecific(vec,VEC_COOKIE,1);
  PetscValidScalarPointer(array,3);
  PetscValidType(vec,1);
  ierr = VecGetLocalSize(vec,&lsize); CHKERRQ(ierr);
  ierr = VecGetArray(vec,&a); CHKERRQ(ierr);
  n = PetscMin(lsize, n);
  ierr = PetscMemcpy(a,array,n*sizeof(PetscScalar)); CHKERRQ(ierr);
  ierr = VecRestoreArray(vec,&a); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt n, const PetscScalar array[]);


ARRAY_FLAT(PetscInt n, PetscScalar array[],
	   ARRAY_INPUT, PyPetsc_SCALAR)

PETSC_OVERRIDE(
PetscErrorCode,
VecPlaceArray,(Vec vec, PetscInt n, PetscScalar array[]), {
  PetscErrorCode ierr;
  PetscInt lsize;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(vec,VEC_COOKIE,1);
  PetscValidScalarPointer(array,3);
  PetscValidType(vec,1);
  ierr = VecGetLocalSize(vec, &lsize);CHKERRQ(ierr);
  if (lsize != n) SETERRQ(1, "cannot place input array, invalid size");
  ierr = VecPlaceArray(vec, array);CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%clear (PetscInt n, PetscScalar array[]);


PetscErrorCode VecResetArray(Vec vec);

/* ---------------------------------------------------------------- */

%wrapper %{

PyObject* Vec__array_interface__(Vec vec) {
  PetscTruth    flag;
  PetscInt      size;
  PetscScalar   *array;
  PyArray_Descr *descr;
  PyObject      *dict;
  /* get vector data*/
  VecValid(vec,&flag);
  if (!flag) {
    PyErr_SetString(_PyExc_PetscError, "vector is not valid");
    return NULL;
  }
  if (!vec->petscnative) {
    PyErr_SetString(_PyExc_PetscError, "vector is not native");
    return NULL;
  }
  VecGetLocalSize(vec, &size);
  VecGetArray(vec, &array);
  VecRestoreArray(vec, &array);
  /* build interface dict */
  descr = PyArray_DescrFromType(PyPetscArray_SCALAR);
  dict  = Py_BuildValue("{sNsNsNsN}",
#if defined(PETSC_USE_64BIT_INDICES)
			"shape",   Py_BuildValue("(L)", size),
#else
			"shape",   Py_BuildValue("(i)", size),
#endif
			"typestr", PyString_FromFormat("%c%c%d", 
						       descr->byteorder,
						       descr->kind, 
						       descr->elsize),
			"data",    Py_BuildValue("NO", PyLong_FromVoidPtr((void*)array), Py_False),
			"version", PyInt_FromLong(3));
  Py_XDECREF(descr);
  return dict;
}
%}

PyObject* Vec__array_interface__(Vec vec);

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
PetscErrorCode VecStrideMin(Vec,PetscInt,PetscInt*,PetscReal*);
PetscErrorCode VecStrideMax(Vec,PetscInt,PetscInt*,PetscReal*);
PetscErrorCode VecStrideScale(Vec,PetscInt,PetscScalar);
PetscErrorCode VecStrideGather(Vec,PetscInt,Vec,InsertMode);
PetscErrorCode VecStrideScatter(Vec,PetscInt,Vec,InsertMode);

/* ---------------------------------------------------------------- */

%typemap(in, numinputs=0, noblock=1) 
PetscReal* norm
($*ltype temp[2])  { $1 = temp; }

%typemap(argout, noblock=1, fragment=SWIG_From_frag(PetscReal))
(NormType vec_norm_type, PetscReal* norm)  {
  %append_output(SWIG_From(PetscReal)($2[0]));
  if ($1 == NORM_1_AND_2)
    %append_output(SWIG_From(PetscReal)($2[1]));
}

PetscErrorCode VecNorm(Vec, NormType vec_norm_type, PetscReal* norm);
PetscErrorCode VecNormBegin(Vec, NormType vec_norm_type, PetscReal* norm);
PetscErrorCode VecNormEnd(Vec, NormType vec_norm_type, PetscReal* norm);
PetscErrorCode VecStrideNorm(Vec, PetscInt, NormType vec_norm_type, PetscReal* norm);

%clear PetscReal* norm;

%ignore VecNormComposedDataID;

/* ---------------------------------------------------------------- */

%typemap(in, numinputs=0, noblock=1) 
PetscScalar* result ($*ltype temp = 0)  { $1 = &temp; }
%typemap(argout, noblock=1, fragment=SWIG_From_frag(PetscScalar)) 
PetscScalar* result {  }

PetscErrorCode VecDot(Vec,Vec,PetscScalar*);
PetscErrorCode VecDotBegin(Vec,Vec,PetscScalar* result);
PetscErrorCode VecDotEnd(Vec,Vec,PetscScalar*); 
PetscErrorCode VecTDot(Vec,Vec,PetscScalar*);
PetscErrorCode VecTDotBegin(Vec,Vec,PetscScalar* result);
PetscErrorCode VecTDotEnd(Vec,Vec,PetscScalar*);

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
