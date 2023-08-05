/* $Id$ */

/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT)

PetscErrorCode ISCreateGeneral(MPI_Comm,PetscInt,const PetscInt[],IS* CREATE);
PetscErrorCode ISCreateBlock(MPI_Comm,PetscInt,PetscInt,const PetscInt[],IS* CREATE);
PetscErrorCode ISCreateStride(MPI_Comm,PetscInt,PetscInt,PetscInt,IS* CREATE);

%clear (PetscInt, const PetscInt[]);

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

PetscErrorCode ISDestroy(IS);

PetscErrorCode ISSetPermutation(IS);
PetscErrorCode ISPermutation(IS,PetscTruth*); 
PetscErrorCode ISSetIdentity(IS);
PetscErrorCode ISIdentity(IS,PetscTruth*);

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
//PetscErrorCode ISRestoreIndices(IS,PetscInt *[]);
PetscErrorCode ISGetSize(IS,PetscInt*);
PetscErrorCode ISGetLocalSize(IS,PetscInt*);
PetscErrorCode ISInvertPermutation(IS, PetscInt, IS* NEWOBJ);


PetscErrorCode ISView(IS,PetscViewer);
PetscErrorCode ISEqual(IS,IS,PetscTruth*);
PetscErrorCode ISSort(IS);
PetscErrorCode ISSorted(IS,PetscTruth*);
PetscErrorCode ISDifference(IS,IS,IS* NEWOBJ);
PetscErrorCode ISSum(IS* INOUT,IS);
PetscErrorCode ISExpand(IS,IS,IS* NEWOBJ);

PetscErrorCode ISBlock(IS,PetscTruth*);
//PetscErrorCode ISBlockGetIndices(IS,PetscInt *[]);
//PetscErrorCode ISBlockRestoreIndices(IS,PetscInt *[]);
PetscErrorCode ISBlockGetSize(IS,PetscInt*);
PetscErrorCode ISBlockGetBlockSize(IS,PetscInt*);

PetscErrorCode ISStride(IS,PetscTruth*);
PetscErrorCode ISStrideGetInfo(IS,PetscInt*,PetscInt*);

PetscErrorCode ISStrideToGeneral(IS);

PetscErrorCode ISDuplicate(IS, IS* NEWOBJ);
PetscErrorCode ISAllGather(IS, IS* NEWOBJ);
//PetscErrorCode ISAllGatherIndices(MPI_Comm,PetscInt,const PetscInt[],PetscInt*,PetscInt*[]);

%wrapper %{

PyObject* IS__array_interface__(IS is) {
  int           ierr;
  PetscTruth    flag;
  PetscInt      size;
  PetscInt      *array;
  PyArray_Descr *descr;
  PyObject      *dict;

  ierr = ISGetLocalSize(is, &size);
  if (ierr) {
    PyErr_SetString(_PyExc_PetscError, "index set is not valid, cannot get array view");
    return NULL;
  }
  ISStride(is, &flag);
  if (flag) {
    PyErr_SetString(_PyExc_PetscError, "index set is strided, cannot get array view");
    return NULL;
  }
  ISBlock(is, &flag);
  if (flag) {
    PyErr_SetString(_PyExc_PetscError, "index set is blocked, cannot get array view");
    return NULL;
  }
  ISGetIndices(is, &array);
  ISRestoreIndices(is, &array);
  /* build interface dict */
  descr = PyArray_DescrFromType(PyPetscArray_INT);
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

PyObject* IS__array_interface__(IS is);

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
