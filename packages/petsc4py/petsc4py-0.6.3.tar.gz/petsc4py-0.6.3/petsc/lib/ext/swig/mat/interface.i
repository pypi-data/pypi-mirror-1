/* $Id$ */


/* ---------------------------------------------------------------- */

PetscErrorCode MatCreate(MPI_Comm, Mat* CREATE);
PetscErrorCode MatDestroy(Mat);
PetscErrorCode MatView(Mat,PetscViewer);


%wrapper %{
#define MatCreateSeqDense(comm, m, n, mat) \
        MatCreateSeqDense(comm, m, n, PETSC_NULL, mat)
%}
PetscErrorCode MatCreateSeqDense(MPI_Comm comm,
				 PetscInt m, PetscInt n,
				 Mat* CREATE);
%wrapper %{
#define MatCreateMPIDense(comm, m, n, M, N, mat) \
        MatCreateMPIDense(comm, m, n, M, N, PETSC_NULL, mat)
%}
PetscErrorCode MatCreateMPIDense(MPI_Comm comm,
				 PetscInt m, PetscInt n, PetscInt M, PetscInt N,
				 Mat* CREATE);

ARRAY_RAW(value_t VALUE[],
	  ARRAY_INPUT, PyPetsc_INT);

%apply value_t VALUE[] {
  const PetscInt nnz[],
  const PetscInt d_nnz[],
  const PetscInt o_nnz[]
};

PetscErrorCode MatCreateSeqAIJ(MPI_Comm,
			       PetscInt, PetscInt,
			       PetscInt, const PetscInt nnz[],
			       Mat* CREATE);

PetscErrorCode MatCreateSeqBAIJ(MPI_Comm,
				PetscInt,
				PetscInt, PetscInt,
				PetscInt, const PetscInt nnz[],
				Mat* CREATE);

PetscErrorCode MatCreateSeqSBAIJ(MPI_Comm,
				 PetscInt,
				 PetscInt, PetscInt,
				 PetscInt, const PetscInt nnz[],
				 Mat* CREATE);

PetscErrorCode MatCreateMPIAIJ(MPI_Comm,
			       PetscInt, PetscInt, PetscInt, PetscInt,
			       PetscInt, const PetscInt d_nnz[],
			       PetscInt, const PetscInt o_nnz[],
			       Mat* CREATE);

PetscErrorCode MatCreateMPIBAIJ(MPI_Comm,
				PetscInt,
				PetscInt, PetscInt, PetscInt, PetscInt,
				PetscInt, const PetscInt d_nnz[],
				PetscInt, const PetscInt o_nnz[],
				Mat* CREATE);

PetscErrorCode MatCreateMPISBAIJ(MPI_Comm,
				 PetscInt,
				 PetscInt, PetscInt, PetscInt, PetscInt,
				 PetscInt, const PetscInt d_nnz[],
				 PetscInt, const PetscInt o_nnz[],
				 Mat* CREATE);

%clear const PetscInt nnz[], const PetscInt d_nnz[], const PetscInt o_nnz[];


PetscErrorCode MatCreateNormal(Mat, Mat* CREATE);


PetscErrorCode MatCreateScatter(MPI_Comm comm, VecScatter scatter, Mat *CREATE);
PetscErrorCode MatScatterSetVecScatter(Mat mat, VecScatter scatter);

PetscErrorCode MatCreateIS(MPI_Comm comm,
			   PetscInt m, PetscInt n, PetscInt M, PetscInt N,
			   ISLocalToGlobalMapping map, Mat *CREATE);
PetscErrorCode MatISGetLocalMat(Mat, Mat* NEWREF);


/* ---------------------------------------------------------------- */

PetscErrorCode MatSetOptionsPrefix(Mat,const char[]);
PetscErrorCode MatAppendOptionsPrefix(Mat,const char[]);
PetscErrorCode MatGetOptionsPrefix(Mat,const char*[]);
PetscErrorCode MatSetFromOptions(Mat);
PetscErrorCode MatSetUp(Mat);

/* ---------------------------------------------------------------- */

PetscErrorCode MatSetSizes(Mat,PetscInt,PetscInt,PetscInt,PetscInt);
PetscErrorCode MatGetSize(Mat,PetscInt*,PetscInt*);
PetscErrorCode MatGetLocalSize(Mat,PetscInt*,PetscInt*);

PetscErrorCode MatSetBlockSize(Mat,PetscInt);
PetscErrorCode MatGetBlockSize(Mat,PetscInt*);

PetscErrorCode MatGetOwnershipRange(Mat,PetscInt*,PetscInt*);

PetscErrorCode MatSetType(Mat,MatType);
PetscErrorCode MatGetType(Mat,MatType*);

PetscErrorCode MatSetUpPreallocation(Mat);

PetscErrorCode MatSetOption(Mat,MatOption);

/* ---------------------------------------------------------------- */

//PetscErrorCode MatValid(Mat,PetscTruth*);
PetscErrorCode MatIsSymmetric(Mat,PetscReal,PetscTruth*);
PetscErrorCode MatIsStructurallySymmetric(Mat,PetscTruth*);
PetscErrorCode MatIsHermitian(Mat,PetscTruth*);
PetscErrorCode MatIsSymmetricKnown(Mat,PetscTruth*,PetscTruth*);
PetscErrorCode MatIsHermitianKnown(Mat,PetscTruth*,PetscTruth*);

PetscErrorCode MatIsTranspose(Mat A,Mat B,PetscReal tol,PetscTruth *flg);

/* ---------------------------------------------------------------- */

PetscErrorCode MatCompress(Mat);
PetscErrorCode MatDuplicate(Mat, MatDuplicateOption, Mat* NEWOBJ);
PetscErrorCode MatCopy(Mat, Mat, MatStructure);

%typemap(in) MatType outtype {
  if ($input == Py_None) $1 = NULL;
  else {
    $1 = PyString_AsString($input);
    if (PyErr_Occurred())
      %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  }
}
PetscErrorCode MatLoad(PetscViewer, MatType outtype, Mat* NEWOBJ);
%clear MatType outtype;


%apply Mat* REUSE { Mat* newmat };

PETSC_OVERRIDE(
PetscErrorCode,
MatConvert,(Mat mat, MatType newtype, Mat *newmat), {
  MatReuse reuse;
  if (!newmat) return 0;
  if (*newmat == PETSC_NULL)
    reuse = MAT_INITIAL_MATRIX;
  else
    reuse = MAT_REUSE_MATRIX;
  return MatConvert(mat, newtype, reuse, newmat);
})

%clear Mat *newmat;


PetscErrorCode MatComputeExplicitOperator(Mat, Mat* NEWOBJ);

/* ---------------------------------------------------------------- */

%wrapper %{
#define  MatGetVecLeft(mat, vec)  MatGetVecs((mat),PETSC_NULL,(vec))
#define  MatGetVecRight(mat, vec) MatGetVecs((mat),(vec),PETSC_NULL)
%}
PetscErrorCode MatGetVecs(Mat, Vec* NEWOBJ, Vec* NEWOBJ);
PetscErrorCode MatGetVecLeft(Mat, Vec* NEWOBJ);
PetscErrorCode MatGetVecRight(Mat, Vec* NEWOBJ);
%wrapper %{
#undef  MatGetVecLeft
#undef  MatGetVecRight
%}

/* ---------------------------------------------------------------- */

#if 0
PetscErrorCode
MatSeqDenseSetPreallocation(Mat, PetscScalar data[]);

PetscErrorCode
MatMPIDenseSetPreallocation(Mat, PetscScalar data[]);
#endif


ARRAY_RAW(value_t VALUE[],
	  ARRAY_INPUT, PyPetsc_INT);

%apply value_t VALUE[] {
  const PetscInt nnz[],
  const PetscInt d_nnz[],
  const PetscInt o_nnz[]
};

PetscErrorCode MatSeqAIJSetPreallocation(Mat,PetscInt,const PetscInt nnz[]);
PetscErrorCode MatSeqBAIJSetPreallocation(Mat,PetscInt,PetscInt,const PetscInt nnz[]);
PetscErrorCode MatSeqSBAIJSetPreallocation(Mat,PetscInt,PetscInt,const PetscInt nnz[]);
PetscErrorCode MatMPIAIJSetPreallocation(Mat,PetscInt, const PetscInt d_nnz[],PetscInt,const PetscInt o_nnz[]);
PetscErrorCode MatMPIBAIJSetPreallocation(Mat,PetscInt,PetscInt, const PetscInt d_nnz[],PetscInt,const PetscInt o_nnz[]);
PetscErrorCode MatMPISBAIJSetPreallocation(Mat,PetscInt,PetscInt,const PetscInt d_nnz[],PetscInt,const PetscInt o_nnz[]);

%clear const PetscInt nnz[],   \
       const PetscInt d_nnz[], \
       const PetscInt o_nnz[];


ARRAY_RAW(value_t INDEX[],
	  ARRAY_INPUT, PyPetsc_INT);
ARRAY_RAW(value_t VALUE[],
	  ARRAY_INPUT, PyPetsc_SCALAR);

%apply value_t INDEX[] { const PetscInt i[], const PetscInt j[] };
%apply value_t VALUE[] { const PetscScalar v[] };
PetscErrorCode MatSeqAIJSetPreallocationCSR(Mat,
					    const PetscInt    i[], 
					    const PetscInt    j[], 
					    const PetscScalar v[]);

%wrapper %{
static
PetscErrorCode MatSeqBAIJSetPreallocationCSR(Mat A,
					     const PetscInt    i[], 
					     const PetscInt    j[], 
					     const PetscScalar v[])
{
  PetscFunctionBegin;
  SETERRQ(1,"Not implemented yet");
  PetscFunctionReturn(0);
}
%}
PetscErrorCode MatSeqBAIJSetPreallocationCSR(Mat,
					     const PetscInt    i[], 
					     const PetscInt    j[], 
					     const PetscScalar v[]);
PetscErrorCode MatMPIAIJSetPreallocationCSR(Mat,
					    const PetscInt    i[], 
					    const PetscInt    j[], 
					    const PetscScalar v[]);
PetscErrorCode MatMPIBAIJSetPreallocationCSR(Mat, PetscInt bs,
					     const PetscInt    i[], 
					     const PetscInt    j[], 
					     const PetscScalar v[]);
%clear const PetscInt    i[], \
       const PetscInt    j[], \
       const PetscScalar v[];


/* ---------------------------------------------------------------- */

PetscErrorCode MatNorm(Mat mat, NormType mat_norm_type, PetscReal *nrm);

/* ---------------------------------------------------------------- */

PetscErrorCode MatZeroEntries(Mat);

PetscErrorCode MatSetLocalToGlobalMapping(Mat,ISLocalToGlobalMapping);
PetscErrorCode MatSetLocalToGlobalMappingBlock(Mat,ISLocalToGlobalMapping);

PETSC_OVERRIDE(
PetscErrorCode,
MatSetValue,
(Mat mat,PetscInt r,PetscInt c,PetscScalar v,InsertMode im), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MatSetValues(mat,1,&r,1,&c,&v,im); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
MatSetValueLocal,
(Mat mat,PetscInt r,PetscInt c,PetscScalar v,InsertMode im), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MatSetValuesLocal(mat,1,&r,1,&c,&v,im); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

%ignore MatSetValue_Row;
%ignore MatSetValue_Column;
%ignore MatSetValue_Value;


ARRAY_FLAT(PetscInt, const PetscInt[],  ARRAY_INPUT, PyPetsc_INT);
ARRAY_RAW(const PetscScalar[],          ARRAY_INPUT, PyPetsc_SCALAR);
%typemap(check)
     (PetscInt,const PetscInt[],
      PetscInt,const PetscInt[],
      const PetscScalar[])
{ ARRAY_check_size(array6, ($1*$3)); }


PetscErrorCode MatSetValues(Mat,
			    PetscInt,const PetscInt[],
			    PetscInt,const PetscInt[],
			    const PetscScalar[],
			    InsertMode);

PetscErrorCode MatSetValuesLocal(Mat,
				 PetscInt,const PetscInt[],
				 PetscInt,const PetscInt[],
				 const PetscScalar[],
				 InsertMode);


%clear (PetscInt, const PetscInt[]);
%clear  const PetscScalar[];
%clear (PetscInt, const PetscInt[],
	PetscInt, const PetscInt[],
	const PetscScalar[]);
 


ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT);
ARRAY_RAW(const PetscScalar[],
	  ARRAY_INPUT, PyPetsc_SCALAR);
%typemap(check)
     (PetscInt,const PetscInt[],
      PetscInt,const PetscInt[],
      const PetscScalar[])
{
  PetscInt bsize;  MatGetBlockSize(arg1, &bsize);
  if (bsize == -1)
    PETSC_seterr(PETSC_ERR_ORDER, "block size not set");
  ARRAY_check_size(array6, $1*bsize*$3*bsize);
}

PetscErrorCode MatSetValuesBlocked(Mat,
				   PetscInt, const PetscInt[],
				   PetscInt, const PetscInt[],
				   const PetscScalar[],
				   InsertMode);

PetscErrorCode MatSetValuesBlockedLocal(Mat,
					PetscInt, const PetscInt[],
					PetscInt, const PetscInt[],
					const PetscScalar[],
					InsertMode);

%clear (PetscInt, const PetscInt[]);
%clear const PetscScalar[];
%clear (PetscInt, const PetscInt[],
	PetscInt, const PetscInt[],
	const PetscScalar[]);


%wrapper %{
#undef  __FUNCT__
#define __FUNCT__  "MatSetValuesCSR_Private"
static PetscErrorCode
MatSetValuesCSR_Private
(Mat A,
 PetscInt nI, const PetscInt    aI[],
 PetscInt nJ, const PetscInt    aJ[],
 PetscInt nV, const PetscScalar aV[],
 InsertMode imode)
{
  PetscInt       k;
  PetscInt       m,n;
  PetscInt       ncols;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  PetscValidHeaderSpecific(A,MAT_COOKIE,1);
  PetscValidIntPointer(aI,2);
  PetscValidIntPointer(aJ,3);
  PetscValidScalarPointer(aV,4);

  ierr = MatGetLocalSize(A,&m,&n);CHKERRQ(ierr);
  if (nI-1 != m)
    SETERRQ2(PETSC_ERR_ARG_OUTOFRANGE,
	     "I size must be %D, it is %D",m+1,nI);
  if (aI[0] != 0)
    SETERRQ1(PETSC_ERR_ARG_OUTOFRANGE,
	     "I[0] must be 0, it is %D",aI[0]);
  if (nJ != aI[nI-1])
    SETERRQ3(PETSC_ERR_ARG_OUTOFRANGE,
	     "J size %D must be I[nI-1], nI is %D, I[nI-1] is %D",
	     nJ, nI, aI[nI-1]);
  if (nJ != nV)
    SETERRQ2(PETSC_ERR_ARG_OUTOFRANGE,
	     "J size %D and V size %D must be the same",nJ,nV);
  for (k=0; k<nI-1; k++) {
    ncols = aI[k+1]- aI[k];
    ierr  = MatSetValues(A,1,&k,ncols,aJ+aI[k],aV+aI[k],imode);CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
}
%}

%wrapper %{
#define MatSetValuesCSR MatSetValuesCSR_Private
%}


ARRAY_FLAT(PetscInt nI, const PetscInt aI[],
	   ARRAY_INPUT, PyPetsc_INT);
ARRAY_FLAT(PetscInt nJ, const PetscInt aJ[],
	   ARRAY_INPUT, PyPetsc_INT);
ARRAY_FLAT(PetscInt nV, const PetscScalar aV[],
	   ARRAY_INPUT, PyPetsc_SCALAR);

PetscErrorCode MatSetValuesCSR(Mat A,
			       PetscInt nI, const PetscInt    aI[],
			       PetscInt nJ, const PetscInt    aJ[],
			       PetscInt nV, const PetscScalar aV[],
			       InsertMode imode);

%clear (PetscInt nI, const PetscInt aI[]);
%clear (PetscInt nJ, const PetscInt aJ[]);
%clear (PetscInt nV, const PetscInt aV[]);

PetscErrorCode MatStoreValues(Mat);
PetscErrorCode MatRetrieveValues(Mat);

/* ---------------------------------------------------------------- */

PetscErrorCode MatAssemblyBegin(Mat,MatAssemblyType);
PetscErrorCode MatAssemblyEnd(Mat,MatAssemblyType);
PetscErrorCode MatAssembled(Mat,PetscTruth*);

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
MatGetValue,
(Mat mat, PetscInt r, PetscInt c, PetscScalar* v), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  ierr = MatGetValues(mat,1,&r,1,&c,v); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT);
ARRAY_RAW(PetscScalar[],
	  ARRAY_OUTPUT, PyPetsc_SCALAR);
%typemap(check)
     (PetscInt, const PetscInt[],
      PetscInt, const PetscInt[],
      PetscScalar[])
{ ARRAY_check_size(array6, ($1*$3)); }


PetscErrorCode MatGetValues(Mat,
			    PetscInt,const PetscInt[],
			    PetscInt,const PetscInt[],
			    PetscScalar[]);

%clear (PetscInt, const PetscInt[]);
%clear PetscScalar[];
%clear (PetscInt, const PetscInt[],
	PetscInt, const PetscInt[],
	PetscScalar[]);

/* ---------------------------------------------------------------- */

%typemap(arginit) PetscInt shift "$1 = 0;";
%typemap(in, numinputs=0) PetscInt shift "";

%typemap(arginit) PetscTruth symm "$1 = PETSC_FALSE;";

%typemap(arginit)
(PetscInt *n, PetscInt *ia[], PetscInt* ja[], PetscTruth* done)
"$1 = NULL; $2 = NULL;  $3 = NULL; $4=NULL;";
%typemap(in, numinputs=0)
(PetscInt *n, PetscInt *ia[], PetscInt* ja[], PetscTruth* done)
(PetscInt n=0, PetscInt* ia=NULL, PetscInt* ja=NULL,
 PetscTruth done=PETSC_FALSE)
"$1 = &n; $2 = &ia;  $3 = &ja; $4 = &done;";
%typemap(argout)
(PetscInt *n, PetscInt *ia[], PetscInt* ja[], PetscTruth* done)
{
  PyObject* o = NULL;
  if (*$4) {
    PyObject* ai = NULL;
    PyObject* aj = NULL;
    ai = ARRAY_NEW(*$2, PyPetsc_INT, 1, (*$1)+1);
    aj = ARRAY_NEW(*$3, PyPetsc_INT, 1, (*$2)[(*$1)]);
    o = Py_BuildValue("(NN)", ai, aj);
  } else {
    o = Py_BuildValue("(OO)", Py_None, Py_None);
  }
  if (PyErr_Occurred())
    %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  %append_output(o);
}
%typemap(freearg, noblock=1)
(PetscInt *n, PetscInt *ia[], PetscInt* ja[], PetscTruth* done)
{ MatRestoreRowIJ(arg1, 0, arg3, $1, $2, $3, $4); };

PetscErrorCode MatGetRowIJ(Mat mat, PetscInt shift, PetscTruth symm,
			   PetscInt* n, PetscInt* ia[], PetscInt* ja[],
			   PetscTruth *done);

%typemap(freearg, noblock=1)
(PetscInt *n, PetscInt *ia[], PetscInt* ja[], PetscTruth* done)
{ MatRestoreColumnIJ(arg1, 0, arg3, $1, $2, $3, $4); };

PetscErrorCode MatGetColumnIJ(Mat mat, PetscInt shift, PetscTruth symm,
			      PetscInt* n, PetscInt* ia[], PetscInt* ja[],
			      PetscTruth *done);

%clear PetscInt shift;
%clear PetscTruth symm;
%clear (PetscInt* n, PetscInt* ia[], PetscInt* ja[], PetscTruth* done);

%ignore MatGetRowIJ;
%ignore MatRestoreRowIJ;
%ignore MatGetColumnIJ;
%ignore MatRestoreColumnIJ;

/* ---------------------------------------------------------------- */

PetscErrorCode MatPermute(Mat, IS, IS, Mat* NEWOBJ);

PetscErrorCode MatPermuteSparsify(Mat,
				  PetscInt, PetscReal, PetscReal,
				  IS, IS,
				  Mat* NEWOBJ);

/* ---------------------------------------------------------------- */

%apply Mat *NEWOBJ { Mat* B }

PETSC_OVERRIDE(
PetscErrorCode,
MatTranspose,
(Mat A, PetscTruth inplace, Mat* B), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (inplace) {
    if (B) *B = PETSC_NULL;
    ierr = MatTranspose(A, PETSC_NULL); CHKERRQ(ierr);
  }
  else {
    ierr = MatTranspose(A, B); CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})

%clear Mat* B;

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
MatIncreaseOverlap,(Mat mat,  IS* INOUT, PetscInt ov), {
  return MatIncreaseOverlap(mat, 1, INOUT, ov);
})


%apply Mat* REUSE { Mat* submat };

PETSC_OVERRIDE(
PetscErrorCode,
MatGetSubMatrix,(Mat mat,
		 IS isrow, IS iscol, PetscInt csize,
		 Mat* submat), {
  MatReuse reuse;
  if (!submat) return 0;
  if (*submat == PETSC_NULL)
    reuse = MAT_INITIAL_MATRIX;
  else
    reuse = MAT_REUSE_MATRIX;
  return MatGetSubMatrix(mat, isrow, iscol, csize,
			 reuse, submat);
})

PETSC_OVERRIDE(
PetscErrorCode,
MatGetSubMatrixSeq,(Mat mat, IS isrow, IS iscol, Mat* submat), {
  MatReuse       scall;
  Mat            *smat;
  PetscErrorCode ierr;
  PetscFunctionBegin;
  if (!submat) return 0;
  smat = submat;
  if (smat[0]) scall = MAT_REUSE_MATRIX;
  else         scall = MAT_INITIAL_MATRIX;
  ierr = MatGetSubMatrices(mat,1,&isrow,&iscol,scall,&smat);CHKERRQ(ierr);
  *submat = smat[0];
  if (scall == MAT_INITIAL_MATRIX) {
    ierr = PetscObjectReference((PetscObject)smat[0]);CHKERRQ(ierr);
    ierr = MatDestroyMatrices(1,&smat);CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
})


%clear Mat* submat;

%ignore MatGetSubMatrices;
%ignore MatDestroyMatrices;

/* ---------------------------------------------------------------- */

%apply Mat* REUSE { Mat* outmat };

PETSC_OVERRIDE(
PetscErrorCode,
MatMerge,(MPI_Comm comm, Mat inmat, PetscInt n, Mat *outmat), {
  MatReuse reuse;
  if (*outmat == PETSC_NULL)
    reuse = MAT_INITIAL_MATRIX;
  else
    reuse = MAT_REUSE_MATRIX;
  return MatMerge(comm, inmat, n, reuse, outmat);
})

%clear Mat* outmat;

/* ---------------------------------------------------------------- */

%apply Mat* REUSE { Mat* multmat };

PETSC_OVERRIDE(
PetscErrorCode,
MatMatMult,(Mat A, Mat B, PetscReal fill, Mat* multmat), {
  MatReuse reuse;
  if (*multmat == PETSC_NULL)
    reuse = MAT_INITIAL_MATRIX;
  else
    reuse = MAT_REUSE_MATRIX;
  return MatMatMult(A, B, reuse, fill, multmat);
})

PETSC_OVERRIDE(
PetscErrorCode,
MatMatMultTranspose,(Mat A,Mat B,PetscReal fill, Mat* multmat), {
  MatReuse reuse;
  if (*multmat == PETSC_NULL)
    reuse = MAT_INITIAL_MATRIX;
  else
    reuse = MAT_REUSE_MATRIX;
  return MatMatMultTranspose(A, B, reuse, fill, multmat);
})

%clear Mat* multmat;


PetscErrorCode MatMatMultSymbolic(Mat,Mat,PetscReal,Mat* NEWOBJ);
PetscErrorCode MatMatMultNumeric(Mat,Mat,Mat);

/* ---------------------------------------------------------------- */

PetscErrorCode MatZeroRowsIS(Mat,IS,PetscScalar);
PetscErrorCode MatZeroRowsLocalIS(Mat,IS,PetscScalar);

ARRAY_FLAT(PetscInt numRows, const PetscInt rows[], ARRAY_INPUT, PyPetsc_INT);
PetscErrorCode MatZeroRows(Mat mat,
			   PetscInt numRows,const PetscInt rows[],
			   PetscScalar diag);
PetscErrorCode MatZeroRowsLocal(Mat mat,
				PetscInt numRows,const PetscInt rows[],
				PetscScalar diag);
%clear (PetscInt numRows,const PetscInt rows[]);

/* ---------------------------------------------------------------- */

PetscErrorCode MatUseScaledForm(Mat,PetscTruth);
PetscErrorCode MatScaleSystem(Mat, Vec OBJ_OR_NONE, Vec OBJ_OR_NONE);
PetscErrorCode MatUnScaleSystem(Mat, Vec OBJ_OR_NONE, Vec OBJ_OR_NONE);

/* ---------------------------------------------------------------- */
%wrapper %{
EXTERN_C_BEGIN
SWIGINTERNINLINE void
_matfactorinfo_input(const PetscReal* info,
		     MatFactorInfo* factorinfo){
  factorinfo->shiftnz        = info[0];
  factorinfo->shiftpd        = info[1];
  factorinfo->shift_fraction = info[2];
  factorinfo->diagonal_fill  = info[3];
  factorinfo->dt             = info[4];
  factorinfo->dtcol          = info[5];
  factorinfo->dtcount        = info[6];
  factorinfo->fill           = info[7];
  factorinfo->levels         = info[8];
  factorinfo->pivotinblocks  = info[9];
  factorinfo->zeropivot      = info[10];
}
SWIGINTERNINLINE void
_matfactorinfo_output(const MatFactorInfo* factorinfo, 
		      PetscReal* info) {
  if (info == NULL) return;
  info[ 0] = factorinfo->shiftnz;
  info[ 1] = factorinfo->shiftpd;
  info[ 2] = factorinfo->shift_fraction;
  info[ 3] = factorinfo->diagonal_fill ;
  info[ 4] = factorinfo->dt;
  info[ 5] = factorinfo->dtcol;
  info[ 6] = factorinfo->dtcount;
  info[ 7] = factorinfo->fill;
  info[ 8] = factorinfo->levels;
  info[ 9] = factorinfo->pivotinblocks;
  info[10] = factorinfo->zeropivot;
}
EXTERN_C_END
%}

%typemap(in, noblock=1) MatFactorInfo* 
($*ltype temp, PyObject* array = NULL, PetscReal* info=NULL) {
  if ($input == Py_None) {
    MatFactorInfoInitialize(&temp);
  } else {
    array = ARRAY_IO($input, PyPetsc_REAL);
    if (PyErr_Occurred())
      %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
    ARRAY_check_size(array, 11);
    _matfactorinfo_input(info, &temp);
  }
  $1=&temp;
}

%typemap(argout, noblock=1) MatFactorInfo* {
  _matfactorinfo_output(&temp$argnum, info$argnum);
}

%typemap(freearg, noblock=1) MatFactorInfo* {
  Py_XDECREF(array$argnum);
}

PetscErrorCode MatGetOrdering(Mat,const MatOrderingType,IS* NEWOBJ,IS* NEWOBJ);
PetscErrorCode MatReorderForNonzeroDiagonal(Mat,PetscReal,IS,IS);

PetscErrorCode MatCholeskyFactor(Mat,IS,MatFactorInfo*);
PetscErrorCode MatCholeskyFactorSymbolic(Mat,IS,MatFactorInfo*,Mat* NEWOBJ);
PetscErrorCode MatCholeskyFactorNumeric(Mat,MatFactorInfo*,Mat* INPUT);

PetscErrorCode MatLUFactor(Mat,IS,IS,MatFactorInfo*);
PetscErrorCode MatILUFactor(Mat,IS,IS,MatFactorInfo*);
PetscErrorCode MatICCFactor(Mat,IS,MatFactorInfo*);
PetscErrorCode MatLUFactorSymbolic(Mat,IS,IS,MatFactorInfo*,Mat* NEWOBJ);
PetscErrorCode MatILUFactorSymbolic(Mat,IS,IS,MatFactorInfo*,Mat* NEWOBJ);
PetscErrorCode MatICCFactorSymbolic(Mat,IS,MatFactorInfo*,Mat* NEWOBJ);
PetscErrorCode MatLUFactorNumeric(Mat,MatFactorInfo*,Mat* INPUT);
PetscErrorCode MatILUDTFactor(Mat,IS,IS,MatFactorInfo*,Mat* NEWOBJ);
PetscErrorCode MatGetInertia(Mat,PetscInt*,PetscInt*,PetscInt*);

PetscErrorCode MatSolve(Mat,Vec,Vec);
PetscErrorCode MatForwardSolve(Mat,Vec,Vec);
PetscErrorCode MatBackwardSolve(Mat,Vec,Vec);
PetscErrorCode MatSolveAdd(Mat,Vec,Vec,Vec);
PetscErrorCode MatSolveTranspose(Mat,Vec,Vec);
PetscErrorCode MatSolveTransposeAdd(Mat,Vec,Vec,Vec);

PetscErrorCode MatSetUnfactored(Mat);


#if 0
PETSC_OVERRIDE(
PetscErrorCode,
MatIsFactored,
(Mat A, PetscTruth* flag), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeaderSpecific(mat,MAT_COOKIE,1);
  PetscValidPointer(flag,2);
  *flag = (A->factored) ? PETSC_TRUE : PETSC_FALSE;
  PetscFunctionReturn(0);
})
#endif

#if 0
PetscErrorCode MatSolves(Mat,Vecs,Vecs);
#else
%ignore MatSolves;
#endif

/* ---------------------------------------------------------------- */

PetscErrorCode MatConjugate(Mat);
PetscErrorCode MatRealPart(Mat);
PetscErrorCode MatImaginaryPart(Mat);

/* ---------------------------------------------------------------- */

PetscErrorCode MatEqual(Mat,Mat,PetscTruth*);
PetscErrorCode MatMultEqual(Mat,Mat,PetscInt,PetscTruth*);
PetscErrorCode MatMultAddEqual(Mat,Mat,PetscInt,PetscTruth*);
PetscErrorCode MatMultTransposeEqual(Mat,Mat,PetscInt,PetscTruth*);
PetscErrorCode MatMultTransposeAddEqual(Mat,Mat,PetscInt,PetscTruth*);

/* ---------------------------------------------------------------- */

PetscErrorCode MatDiagonalSet(Mat,Vec,InsertMode);
PetscErrorCode MatDiagonalScale(Mat, Vec OBJ_OR_NONE, Vec OBJ_OR_NONE);

PetscErrorCode MatScale(Mat,PetscScalar);
PetscErrorCode MatShift(Mat,PetscScalar);

PetscErrorCode MatAXPY(Mat,PetscScalar,Mat,MatStructure);
PetscErrorCode MatAYPX(Mat,PetscScalar,Mat,MatStructure);

PetscErrorCode MatInterpolate(Mat,Vec,Vec);
PetscErrorCode MatInterpolateAdd(Mat,Vec,Vec,Vec);
PetscErrorCode MatRestrict(Mat,Vec,Vec);

/* ---------------------------------------------------------------- */

PetscErrorCode MatGetDiagonal(Mat,Vec);
PetscErrorCode MatGetRowMax(Mat,Vec);

PetscErrorCode MatGetColumnVector(Mat,Vec,PetscInt);

/* ---------------------------------------------------------------- */

PetscErrorCode MatMult(Mat,Vec,Vec);
PetscErrorCode MatMultAdd(Mat,Vec,Vec,Vec);
PetscErrorCode MatMultTranspose(Mat,Vec,Vec);
PetscErrorCode MatMultTransposeAdd(Mat,Vec,Vec,Vec);
PetscErrorCode MatMultConstrained(Mat,Vec,Vec);
PetscErrorCode MatMultTransposeConstrained(Mat,Vec,Vec);

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
