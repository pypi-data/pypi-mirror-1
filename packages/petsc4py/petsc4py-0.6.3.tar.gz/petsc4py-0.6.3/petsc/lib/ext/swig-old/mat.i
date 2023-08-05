/* $Id$ */

/* ---------------------------------------------------------------- */

typedef const char* MatType;

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode
MatCreate(MPI_Comm, Mat* CREATE);

%wrapper %{
#define MatCreateSeqDense(comm, m, n, mat) \
        MatCreateSeqDense(comm, m, n, PETSC_NULL, mat)
%}
PetscErrorCode
MatCreateSeqDense(MPI_Comm comm,
		  PetscInt m, PetscInt n,
		  Mat* CREATE);
%ignore MatCreateSeqDense;

%wrapper %{
#define MatCreateMPIDense(comm, m, n, M, N, mat) \
        MatCreateMPIDense(comm, m, n, M, N, PETSC_NULL, mat)
%}
PetscErrorCode
MatCreateMPIDense(MPI_Comm comm,
		  PetscInt m, PetscInt n, PetscInt M, PetscInt N,
		  Mat* CREATE);
%ignore MatCreateMPIDense;

ARRAY_RAW(value_t VALUE[],
	  ARRAY_INPUT, PyPetsc_INT);

%apply value_t VALUE[] {
  const PetscInt nnz[],
  const PetscInt d_nnz[],
  const PetscInt o_nnz[]
};

PetscErrorCode
MatCreateSeqAIJ(MPI_Comm,
		PetscInt, PetscInt,
		PetscInt, const PetscInt nnz[],
		Mat* CREATE);

PetscErrorCode
MatCreateSeqBAIJ(MPI_Comm,
		 PetscInt,
		 PetscInt, PetscInt,
		 PetscInt, const PetscInt nnz[],
		 Mat* CREATE);

PetscErrorCode
MatCreateSeqSBAIJ(MPI_Comm,
		  PetscInt,
		  PetscInt, PetscInt,
		  PetscInt, const PetscInt nnz[],
		  Mat* CREATE);

PetscErrorCode
MatCreateMPIAIJ(MPI_Comm,
		PetscInt, PetscInt, PetscInt, PetscInt,
		PetscInt, const PetscInt d_nnz[],
		PetscInt, const PetscInt o_nnz[],
		Mat* CREATE);

PetscErrorCode
MatCreateMPIBAIJ(MPI_Comm,
		 PetscInt,
		 PetscInt, PetscInt, PetscInt, PetscInt,
		 PetscInt, const PetscInt d_nnz[],
		 PetscInt, const PetscInt o_nnz[],
		 Mat* CREATE);

PetscErrorCode
MatCreateMPISBAIJ(MPI_Comm,
		  PetscInt,
		  PetscInt, PetscInt, PetscInt, PetscInt,
		  PetscInt, const PetscInt d_nnz[],
		  PetscInt, const PetscInt o_nnz[],
		  Mat* CREATE);

%clear const PetscInt nnz[],   \
       const PetscInt d_nnz[], \
       const PetscInt o_nnz[];

PetscErrorCode
MatCreateNormal(Mat, Mat* CREATE);

PetscErrorCode
MatCreateScatter(MPI_Comm comm, VecScatter scatter, Mat *CREATE);

PetscErrorCode
MatScatterSetVecScatter(Mat mat, VecScatter scatter);

PetscErrorCode 
MatCreateIS(MPI_Comm comm,
	    PetscInt m, PetscInt n, PetscInt M, PetscInt N,
	    ISLocalToGlobalMapping map, Mat *CREATE);

PetscErrorCode
MatISGetLocalMat(Mat, Mat* NEWREF);

/* ---------------------------------------------------------------- */



PetscErrorCode
MatDuplicate(Mat, MatDuplicateOption, Mat* NEWOBJ);

PetscErrorCode
MatCopy(Mat, Mat, MatStructure);

%typemap(in) MatType outtype
{
  if ($input == Py_None) $1 = NULL;
  else {
    $1 = PyString_AsString($input);
    if (PyErr_Occurred())
      %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  }
}

PetscErrorCode
MatLoad(PetscViewer, MatType outtype, Mat* NEWOBJ);
%ignore MatLoad;

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


PetscErrorCode
MatComputeExplicitOperator(Mat, Mat* NEWOBJ);

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

%ignore MatGetVecs;
%ignore MatGetVecLeft;
%ignore MatGetVecRight;

/* ---------------------------------------------------------------- */





/* ---------------------------------------------------------------- */

%ignore MatInfo;
%ignore MatGetInfo;

/* ---------------------------------------------------------------- */


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

PetscErrorCode
MatSeqAIJSetPreallocation(Mat,
			  PetscInt, const PetscInt nnz[]);
%ignore MatSeqAIJSetPreallocation;


PetscErrorCode
MatSeqBAIJSetPreallocation(Mat,
			   PetscInt,
			   PetscInt, const PetscInt nnz[]);
%ignore MatSeqBAIJSetPreallocation;


PetscErrorCode
MatSeqSBAIJSetPreallocation(Mat,
			    PetscInt,
			    PetscInt, const PetscInt nnz[]);
%ignore MatSeqSBAIJSetPreallocation;


PetscErrorCode
MatMPIAIJSetPreallocation(Mat,
			  PetscInt, const PetscInt d_nnz[],
			  PetscInt, const PetscInt o_nnz[]);
%ignore MatMPIAIJSetPreallocation;


PetscErrorCode
MatMPIBAIJSetPreallocation(Mat,
			   PetscInt,
			   PetscInt, const PetscInt d_nnz[],
			   PetscInt, const PetscInt o_nnz[]);
%ignore MatMPIBAIJSetPreallocation;

PetscErrorCode
MatMPISBAIJSetPreallocation(Mat,
			    PetscInt,
			    PetscInt, const PetscInt d_nnz[],
			    PetscInt, const PetscInt o_nnz[]);
%ignore MatMPISBAIJSetPreallocation;


%clear const PetscInt nnz[],   \
       const PetscInt d_nnz[], \
       const PetscInt o_nnz[];


ARRAY_RAW(value_t INDEX[],
	  ARRAY_INPUT, PyPetsc_INT);
ARRAY_RAW(value_t VALUE[],
	  ARRAY_INPUT, PyPetsc_SCALAR);

%apply value_t INDEX[] { const PetscInt i[], const PetscInt j[] };
%apply value_t VALUE[] { const PetscScalar v[] };

PetscErrorCode
MatSeqAIJSetPreallocationCSR(Mat,
			     const PetscInt    i[], 
			     const PetscInt    j[], 
			     const PetscScalar v[]);

PetscErrorCode
MatMPIAIJSetPreallocationCSR(Mat,
			     const PetscInt    i[], 
			     const PetscInt    j[], 
			     const PetscScalar v[]);

PetscErrorCode
MatMPIBAIJSetPreallocationCSR(Mat, PetscInt bs,
			      const PetscInt    i[], 
			      const PetscInt    j[], 
			      const PetscScalar v[]);

%clear const PetscInt    i[], \
       const PetscInt    j[], \
       const PetscScalar v[];


/* ---------------------------------------------------------------- */


PetscErrorCode
MatNorm(Mat mat, NormType mat_norm_type, PetscReal *nrm);

%clear NormType mat_norm_type;

/* ---------------------------------------------------------------- */

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


PetscErrorCode
MatSetValues(Mat,
	     PetscInt,const PetscInt[],
	     PetscInt,const PetscInt[],
	     const PetscScalar[],
	     InsertMode);

PetscErrorCode
MatSetValuesLocal(Mat,
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

PetscErrorCode
MatSetValuesBlocked(Mat,
		    PetscInt, const PetscInt[],
		    PetscInt, const PetscInt[],
		    const PetscScalar[],
		    InsertMode);

PetscErrorCode
MatSetValuesBlockedLocal(Mat,
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

PetscErrorCode
MatSetValuesCSR(Mat A,
		PetscInt nI, const PetscInt    aI[],
		PetscInt nJ, const PetscInt    aJ[],
		PetscInt nV, const PetscScalar aV[],
		InsertMode imode);

%clear (PetscInt nI, const PetscInt aI[]);
%clear (PetscInt nJ, const PetscInt aJ[]);
%clear (PetscInt nV, const PetscInt aV[]);

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


PetscErrorCode
MatGetValues(Mat,
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

PetscErrorCode
MatGetRowIJ(Mat mat, PetscInt shift, PetscTruth symm,
	    PetscInt* n, PetscInt* ia[], PetscInt* ja[],
	    PetscTruth *done);

%typemap(freearg, noblock=1)
(PetscInt *n, PetscInt *ia[], PetscInt* ja[], PetscTruth* done)
{ MatRestoreColumnIJ(arg1, 0, arg3, $1, $2, $3, $4); };

PetscErrorCode
MatGetColumnIJ(Mat mat, PetscInt shift, PetscTruth symm,
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

typedef char* MatOrderingType;

%constant MatOrderingType MATORDERING_OWD = MATORDERING_1WD;

PetscErrorCode
MatGetOrdering(Mat,
	       const MatOrderingType,
	       IS* NEWOBJ, IS* NEWOBJ);
%ignore MatGetOrdering;

PetscErrorCode
MatPermute(Mat, IS, IS, Mat* NEWOBJ);

PetscErrorCode
MatPermuteSparsify(Mat,
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

%ignore MatMerge_SeqsToMPI;
%ignore MatMerge_SeqsToMPISymbolic;
%ignore MatMerge_SeqsToMPINumeric;

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

PetscErrorCode
MatMatMultSymbolic(Mat, Mat, PetscReal, Mat* NEWOBJ);

%ignore MatMatMultTransposeSymbolic;
%ignore MatMatMultTransposeNumeric;

/* ---------------------------------------------------------------- */

PetscErrorCode MatZeroRowsIS(Mat,IS,PetscScalar);
PetscErrorCode MatZeroRowsLocalIS(Mat,IS,PetscScalar);

%rename (MatZeroRows)      MatZeroRowsIS;
%rename (MatZeroRowsLocal) MatZeroRowsLocalIS;
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

%ignore MatZeroRows;
%ignore MatZeroRowsLocal;

/* ---------------------------------------------------------------- */

PetscErrorCode MatDiagonalScale(Mat, Vec OBJ_OR_NONE, Vec OBJ_OR_NONE);

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

%ignore MatFactorInfo;
%ignore MatFactorInfoInitialize;

PetscErrorCode MatCholeskyFactorSymbolic(Mat, IS, MatFactorInfo*, Mat* NEWOBJ);

PetscErrorCode MatICCFactorSymbolic(Mat, IS, MatFactorInfo*, Mat* NEWOBJ);

PetscErrorCode MatCholeskyFactorNumeric(Mat, MatFactorInfo*, Mat* INPUT);

PetscErrorCode MatLUFactorSymbolic(Mat, IS, IS, MatFactorInfo*, Mat* NEWOBJ);

PetscErrorCode MatILUFactorSymbolic(Mat, IS, IS, MatFactorInfo*, Mat* NEWOBJ);

PetscErrorCode MatLUFactorNumeric(Mat, MatFactorInfo*, Mat* INPUT);

PetscErrorCode MatILUDTFactor(Mat, IS, IS, MatFactorInfo*, Mat* NEWOBJ);


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


/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore  MAT_FILE_COOKIE;
%ignore  MATSNESMFCTX_COOKIE;
%ignore  MAT_FDCOLORING_COOKIE;
%ignore  MAT_PARTITIONING_COOKIE;

%ignore  MAT_Mult;
%ignore  MAT_MultMatrixFree;
%ignore  MAT_Mults;
%ignore  MAT_MultConstrained;
%ignore  MAT_MultAdd;
%ignore  MAT_MultTranspose;
%ignore  MAT_MultTransposeConstrained;
%ignore  MAT_MultTransposeAdd;
%ignore  MAT_Solve;
%ignore  MAT_Solves;
%ignore  MAT_SolveAdd;
%ignore  MAT_SolveTranspose;
%ignore  MAT_SolveTransposeAdd;
%ignore  MAT_Relax;
%ignore  MAT_ForwardSolve;
%ignore  MAT_BackwardSolve;
%ignore  MAT_LUFactor;
%ignore  MAT_LUFactorSymbolic;
%ignore  MAT_LUFactorNumeric;
%ignore  MAT_CholeskyFactor;
%ignore  MAT_CholeskyFactorSymbolic;
%ignore  MAT_CholeskyFactorNumeric;
%ignore  MAT_ILUFactor;
%ignore  MAT_ILUFactorSymbolic;
%ignore  MAT_ICCFactorSymbolic;
%ignore  MAT_Copy;
%ignore  MAT_Convert;
%ignore  MAT_Scale;
%ignore  MAT_AssemblyBegin;
%ignore  MAT_AssemblyEnd;
%ignore  MAT_SetValues;
%ignore  MAT_GetValues;
%ignore  MAT_GetRow;
%ignore  MAT_GetSubMatrices;
%ignore  MAT_GetColoring;
%ignore  MAT_GetOrdering;
%ignore  MAT_IncreaseOverlap;
%ignore  MAT_Partitioning;
%ignore  MAT_ZeroEntries;
%ignore  MAT_Load;
%ignore  MAT_View;
%ignore  MAT_AXPY;
%ignore  MAT_FDColoringCreate;
%ignore  MAT_FDColoringApply;
%ignore  MAT_Transpose;
%ignore  MAT_FDColoringFunction;
%ignore  MAT_MatMult;
%ignore  MAT_MatMultSymbolic;
%ignore  MAT_MatMultNumeric;
%ignore  MAT_PtAP;
%ignore  MAT_PtAPSymbolic;
%ignore  MAT_PtAPNumeric;
%ignore  MAT_MatMultTranspose;
%ignore  MAT_MatMultTransposeSymbolic;
%ignore  MAT_MatMultTransposeNumeric;

%ignore MatInitializePackage;
%ignore MatRegisterAll;
%ignore MatRegister;
%ignore MatRegisterAllCalled;
%ignore PetscFList;
%ignore MatList;

%ignore MatConvertRegister;
%ignore MatConvertRegisterAllCalled;
%ignore MatConvertRegisterDestroy;
%ignore MatConvertList;

%ignore MatISGetLocalMat;
%ignore MatSeqAIJGetInodeSizes;

%ignore MatOrderingRegister;
%ignore MatOrderingRegisterDestroy;
%ignore MatOrderingRegisterAll;
%ignore MatOrderingRegisterAllCalled;
%ignore MatColoringRegisterAllCalled;
%ignore MatOrderingList;

%ignore MatCreateMPIRowbs;
%ignore MatCreateAdic;
%ignore MatMPIRowbsGetColor;


%ignore MatSolves;

%ignore MatDAADSetCtx;

%ignore MatStencil;
%ignore MatSetValuesStencil;
%ignore MatSetValuesBlockedStencil;
%ignore MatSetStencil;

%ignore MatSetColoring;
%ignore MatSetValuesAdic;
%ignore MatSetValuesAdifor;

%ignore MatGetRow;
%ignore MatRestoreRow;
%ignore MatGetColumn;
%ignore MatRestoreColumn;
%ignore MatGetArray;
%ignore MatRestoreArray;

%ignore MatSORType;
%ignore MatRelax;
%ignore MatPBRelax;

%ignore MatBDiagGetData;
%ignore MatSeqAIJSetColumnIndices;
%ignore MatSeqBAIJSetColumnIndices;
%ignore MatCreateSeqAIJWithArrays;

%ignore MatSeqBAIJSetPreallocation;
%ignore MatSeqSBAIJSetPreallocation;
%ignore MatSeqAIJSetPreallocation;
%ignore MatSeqDensePreallocation;
%ignore MatSeqBDiagSetPreallocation;
%ignore MatSeqDenseSetPreallocation;

//%ignore MatMPIBAIJSetPreallocation;
//%ignore MatMPISBAIJSetPreallocation;
//%ignore MatMPIAIJSetPreallocation;
%ignore MatMPIDensePreallocation;
%ignore MatMPIBDiagSetPreallocation;
%ignore MatMPIAdjSetPreallocation;
%ignore MatMPIDenseSetPreallocation;
%ignore MatMPIRowbsSetPreallocation;

%ignore MatGetCommunicationStructs;

%ignore MatMPIAIJGetSeqAIJ;
%ignore MatMPIBAIJGetSeqBAIJ;
%ignore MatAdicSetLocalFunction;

%ignore MatColoringType;
%ignore MATCOLORING_NATURAL;
%ignore MATCOLORING_SL;
%ignore MATCOLORING_LF;
%ignore MATCOLORING_ID;
%ignore MatGetColoring;
%ignore MatColoringRegister;
%ignore MatColoringRegisterAll;
%ignore MatColoringRegisterDestroy;
%ignore MatColoringPatch;

%ignore MatFDColoringCreate;
%ignore MatFDColoringDestroy;
%ignore MatFDColoringView;
%ignore MatFDColoringSetFunction;
%ignore MatFDColoringSetParameters;
%ignore MatFDColoringSetFrequency;
%ignore MatFDColoringGetFrequency;
%ignore MatFDColoringSetFromOptions;
%ignore MatFDColoringApply;
%ignore MatFDColoringApplyTS;
%ignore MatFDColoringSetRecompute;
%ignore MatFDColoringSetF;
%ignore MatFDColoringGetPerturbedColumns;

%ignore MatPartitioningType;
%ignore MAT_PARTITIONING_CURRENT;
%ignore MAT_PARTITIONING_PARMETIS;
%ignore MAT_PARTITIONING_CHACO;
%ignore MAT_PARTITIONING_JOSTLE;
%ignore MAT_PARTITIONING_PARTY;
%ignore MAT_PARTITIONING_SCOTCH;

%ignore MatPartitioningRegisterAll;
%ignore MatPartitioningRegisterDestroy;
%ignore MatPartitioningRegisterAllCalled;
%ignore MatPartitioningRegister;

%ignore MatPartitioningCreate;
%ignore MatPartitioningSetType;
%ignore MatPartitioningSetNParts;
%ignore MatPartitioningSetAdjacency;
%ignore MatPartitioningSetVertexWeights;
%ignore MatPartitioningSetPartitionWeights;
%ignore MatPartitioningApply;
%ignore MatPartitioningDestroy;
%ignore MatPartitioningView;
%ignore MatPartitioningSetFromOptions;
%ignore MatPartitioningGetType;

%ignore MatPartitioningParmetisSetCoarseSequential;

%ignore MatPartitioningJostleSetCoarseLevel;
%ignore MatPartitioningJostleSetCoarseSequential;

%ignore MPChacoGlobalType;
%ignore MPChacoLocalType;
%ignore MPChacoEigenType;
%ignore MatPartitioningChacoSetGlobal;
%ignore MatPartitioningChacoSetLocal;
%ignore MatPartitioningChacoSetCoarseLevel;
%ignore MatPartitioningChacoSetEigenSolver;
%ignore MatPartitioningChacoSetEigenTol;
%ignore MatPartitioningChacoSetEigenNumber;

%ignore MP_PARTY_OPT;
%ignore MP_PARTY_LIN;
%ignore MP_PARTY_SCA;
%ignore MP_PARTY_RAN;
%ignore MP_PARTY_GBF;
%ignore MP_PARTY_GCF;
%ignore MP_PARTY_BUB;
%ignore MP_PARTY_DEF;
%ignore MatPartitioningPartySetGlobal;
%ignore MP_PARTY_HELPFUL_SETS;
%ignore MP_PARTY_KERNIGHAN_LIN;
%ignore MP_PARTY_NONE;
%ignore MatPartitioningPartySetLocal;
%ignore MatPartitioningPartySetCoarseLevel;
%ignore MatPartitioningPartySetBipart;
%ignore MatPartitioningPartySetMatchOptimization;

%ignore MPScotchGlobalType;
%ignore MPScotchLocalType;
%ignore MatPartitioningScotchSetArch;
%ignore MatPartitioningScotchSetMultilevel;
%ignore MatPartitioningScotchSetGlobal;
%ignore MatPartitioningScotchSetCoarseLevel;
%ignore MatPartitioningScotchSetHostList;
%ignore MatPartitioningScotchSetLocal;
%ignore MatPartitioningScotchSetMapping;
%ignore MatPartitioningScotchSetStrategy;

%ignore PetscViewerMathematicaPutMatrix;
%ignore PetscViewerMathematicaPutCSRMatrix;

%ignore MatMPIBAIJSetHashTableFactor;

/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt, const PetscInt[],
	   ARRAY_INPUT, PyPetsc_INT);
ARRAY_RAW(const PetscScalar[],
	  ARRAY_INPUT, PyPetsc_SCALAR);
%typemap(check)
     (PetscInt,const PetscInt[],
      PetscInt,const PetscInt[],
      const PetscScalar[])
{ ARRAY_check_size(array6, ($1*$3)); }


%wrapper %{
static PetscErrorCode
MatSetValues_Dummy(Mat mat,
		   PetscInt nr,const PetscInt r[],
		   PetscInt nc,const PetscInt c[],
		   const PetscScalar v[],
		   InsertMode im)
{
  PetscFunctionBegin;
  PetscFunctionReturn(0);
}
%}

static PetscErrorCode
MatSetValues_Dummy(Mat,
		   PetscInt,const PetscInt[],
		   PetscInt,const PetscInt[],
		   const PetscScalar[],
		   InsertMode);


%clear (PetscInt, const PetscInt[]);
%clear  const PetscScalar[];
%clear (PetscInt, const PetscInt[],
	PetscInt, const PetscInt[],
	const PetscScalar[]);

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
