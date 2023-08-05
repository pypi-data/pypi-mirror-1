/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

typedef const char* VecType;


PetscErrorCode 
VecCreate(MPI_Comm, Vec* CREATE);

PetscErrorCode 
VecCreateSeq(MPI_Comm, PetscInt, Vec* CREATE);

PetscErrorCode 
VecCreateMPI(MPI_Comm, PetscInt, PetscInt, Vec* CREATE);

PetscErrorCode 
VecCreateShared(MPI_Comm, PetscInt, PetscInt, Vec* CREATE);


ARRAY_FLAT(PetscInt nghost, const PetscInt ghosts[],
	   ARRAY_INPUT, PyPetsc_INT)

PetscErrorCode 
VecCreateGhost(MPI_Comm,
	       PetscInt, PetscInt, 
	       PetscInt nghost, const PetscInt ghosts[],
	       Vec* CREATE);

PetscErrorCode 
VecCreateGhostBlock(MPI_Comm,
		    PetscInt, PetscInt, PetscInt,
		    PetscInt nghost, const PetscInt ghosts[],
		    Vec* CREATE);

%clear (PetscInt nghost, const PetscInt ghosts[]);

%ignore VecCreateSeqWithArray;
%ignore VecCreateMPIWithArray;
%ignore VecCreateGhostWithArray;
%ignore VecCreateGhostBlockWithArray;

PetscErrorCode 
VecDuplicate(Vec, Vec* NEWOBJ);

PetscErrorCode
VecGhostGetLocalForm(Vec, Vec* NEWOBJ);


%typemap(arginit) VecType outtype "$1 = NULL;";
%typemap(in, noblock=1) VecType outtype {
  if ($input!=Py_None) {
    $1 = PyString_AsString($input);
    if (PyErr_Occurred()) SWIG_fail;
  }
}

PetscErrorCode 
VecLoad(PetscViewer, VecType outtype, Vec* NEWOBJ);
%ignore VecLoad; 

%clear VecType outtype;

/* ---------------------------------------------------------------- */




/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT)

ARRAY_RAW(PetscScalar[],
	  ARRAY_OUTPUT, PyPetsc_SCALAR)

%typemap(check) 
     (PetscInt,const PetscInt[],const PetscScalar[])
{ ARRAY_check_size(array4, ($1)); }

PetscErrorCode
VecGetValues(Vec, 
	     PetscInt, const PetscInt[], PetscScalar[]);

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

PetscErrorCode 
VecSetValues(Vec,
	     PetscInt,const PetscInt[],const PetscScalar[],
	     InsertMode);

PetscErrorCode 
VecSetValuesLocal(Vec,
		  PetscInt,const PetscInt[],const PetscScalar[],
		  InsertMode);

%clear (PetscInt, const PetscInt[]);
%clear  const PetscScalar[];
%clear (PetscInt,const PetscInt[],const PetscScalar[]);

/* ---------------------------------------------------------------- */

PetscErrorCode VecSetRandom(Vec, PetscRandom OBJ_OR_NONE);

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


%wrapper %{

PyObject* Vec__array_typestr__(Vec SWIGUNUSEDPARM(vec)) {
  PyArray_Descr *descr = PyArray_DescrFromType(PyPetscArray_SCALAR);
  char kind      = descr->kind;
  char byteorder = descr->byteorder;
  int  elsize    = descr->elsize;
  Py_DECREF(descr);
  return PyString_FromFormat("%c%c%d", byteorder, kind, elsize);
}

PyObject* Vec__array_shape__(Vec vec) {
  PetscTruth flag;
  PetscInt   size;
  VecValid(vec,&flag);
  if (!flag) {
    PyErr_SetString(_PyExc_PetscError, "vector is not valid");
    return NULL;
  }
  VecGetLocalSize(vec, &size);
#if defined(PETSC_USE_64BIT_INDICES)
  return Py_BuildValue("(L)", size);
#else
  return Py_BuildValue("(i)", size);
#endif
}

PyObject* Vec__array_data__(Vec vec) {
  PetscTruth   flag;
  PetscScalar* array;
  VecValid(vec,&flag);
  if (!flag) {
    PyErr_SetString(_PyExc_PetscError, "vector is not valid");
    return NULL;
  }
  if (!vec->petscnative) {
    PyErr_SetString(_PyExc_PetscError, "vector is not native");
    return NULL;
  }
  VecGetArray(vec, &array);
  VecRestoreArray(vec, &array);
  return Py_BuildValue("NO", PyString_FromFormat("%p", (void*)array), Py_False);
}
%}

PyObject* Vec__array_shape__   (Vec vec);
PyObject* Vec__array_data__    (Vec vec);
PyObject* Vec__array_typestr__ (Vec vec);

/* ---------------------------------------------------------------- */

%wrapper %{
#define VecStrideScale(v,start,scale) VecStrideScale(v,start,&scale)
%}
PetscErrorCode VecStrideScale(Vec, PetscInt, PetscScalar);
%ignore VecStrideScale;
%wrapper %{
#undef VecStrideScale
%}

/* ---------------------------------------------------------------- */

%typemap(in, numinputs=0, noblock=1) PetscReal* norm 
($*ltype temp[2])  { $1 = temp; }

%typemap(argout, noblock=1, fragment=SWIG_From_frag(PetscReal))
(NormType vec_norm_type, PetscReal* norm)  {
  %append_output(SWIG_From(PetscReal)($2[0]));
  if ($1 == NORM_1_AND_2)
    %append_output(SWIG_From(PetscReal)($2[1]));
}

PetscErrorCode 
VecNorm(Vec, NormType vec_norm_type, PetscReal* norm);

PetscErrorCode 
VecNormBegin(Vec, NormType vec_norm_type, PetscReal* norm);

PetscErrorCode 
VecNormEnd(Vec, NormType vec_norm_type, PetscReal* norm);

PetscErrorCode 
VecStrideNorm(Vec, PetscInt, NormType vec_norm_type, PetscReal* norm);

%clear PetscReal* norm;

%ignore VecNormComposedDataID;

/* ---------------------------------------------------------------- */

%ignore VecMAXPY;
%ignore VecMDot;
%ignore VecMDotBegin;
%ignore VecMDotEnd;
%ignore VecMTDot;
%ignore VecMTDotBegin;
%ignore VecMTDotEnd;

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore VEC_FILE_COOKIE;
%ignore VEC_View;
%ignore VEC_Max;
%ignore VEC_Min;
%ignore VEC_DotBarrier;
%ignore VEC_Dot;
%ignore VEC_MDotBarrier;
%ignore VEC_MDot;
%ignore VEC_TDot;
%ignore VEC_MTDot;
%ignore VEC_Norm;
%ignore VEC_Normalize;
%ignore VEC_Scale;
%ignore VEC_Copy;
%ignore VEC_Set;
%ignore VEC_AXPY;
%ignore VEC_AYPX;
%ignore VEC_WAXPY;
%ignore VEC_MAXPY;
%ignore VEC_AssemblyEnd;
%ignore VEC_PointwiseMult;
%ignore VEC_SetValues;
%ignore VEC_Load;
%ignore VEC_SetRandom;
%ignore VEC_ReduceArithmetic;
%ignore VEC_ReduceBarrier;
%ignore VEC_ReduceCommunication;
%ignore VEC_Swap;
%ignore VEC_AssemblyBegin;
%ignore VEC_NormBarrier;

%ignore VecList;
%ignore VecRegister;
%ignore VecRegisterAll;
%ignore VecRegisterAllCalled;
%ignore VecRegisterDestroy;
%ignore VecInitializePackage;

%ignore VecSetValue_Row;
%ignore VecSetValue_Value;

%ignore VecGetArray_Private;
%ignore VecRestoreArray_Private;
%ignore VecGetArray4d;
%ignore VecRestoreArray4d;
%ignore VecGetArray3d;
%ignore VecRestoreArray3d;
%ignore VecGetArray2d;
%ignore VecRestoreArray2d;
%ignore VecGetArray1d;
%ignore VecRestoreArray1d;

%ignore VecReplaceArray;
%ignore VecGetArrays;
%ignore VecRestoreArrays;

%ignore VecContourScale;

%ignore VecOperation;
%ignore VecSetOperation;

%ignore PetscViewerMathematicaGetVector;
%ignore PetscViewerMathematicaPutVector;

%ignore _p_Vecs;
%ignore _n_Vecs;

%ignore VecDuplicateVecs;
%ignore VecDestroyVecs;

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
