/* $Id$ */

/* ---------------------------------------------------------------- */
/* PetscTruth */
/* ---------------------------------------------------------------- */
PETSC_ENUM(PetscTruth);
PETSC_ENUM_CHECK_RANGE(PetscTruth, PETSC_FALSE, PETSC_TRUE);
/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* InsertMode */
/* ---------------------------------------------------------------- */
PETSC_ENUM(InsertMode);
PETSC_ENUM_DEFAULT_VALUE(InsertMode, INSERT_VALUES);
PETSC_ENUM_CHECK_RANGE(InsertMode, NOT_SET_VALUES, MAX_VALUES);
/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* ScatterMode */
/* ---------------------------------------------------------------- */
PETSC_ENUM(ScatterMode);
PETSC_ENUM_CHECK_RANGE(ScatterMode, SCATTER_FORWARD, SCATTER_REVERSE);
/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* NormType */
/* ---------------------------------------------------------------- */
PETSC_ENUM(NormType);
PETSC_ENUM_DEFAULT_VALUE(NormType, NORM_2);
PETSC_ENUM_CHECK_RANGE(NormType, NORM_1, NORM_1_AND_2);
PETSC_ENUM_DEFAULT_VALUE(NormType vec_norm_type, NORM_2);
PETSC_ENUM_DEFAULT_VALUE(NormType mat_norm_type, NORM_FROBENIUS);
/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* Viewers */
/* ---------------------------------------------------------------- */
PETSC_ENUM(PetscViewerFormat);
PETSC_ENUM_CHECK_RANGE(PetscViewerFormat,
		       PETSC_VIEWER_ASCII_DEFAULT, 
		       PETSC_VIEWER_ASCII_FACTOR_INFO)
PETSC_ENUM(PetscFileMode);
PETSC_ENUM_CHECK_RANGE(PetscFileMode,
		       FILE_MODE_READ, FILE_MODE_APPEND_UPDATE)
/* From: include/petscdraw.h */
#define PETSC_DRAW_FULL_SIZE    -3
#define PETSC_DRAW_HALF_SIZE    -4
#define PETSC_DRAW_THIRD_SIZE   -5
#define PETSC_DRAW_QUARTER_SIZE -6
/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* IS - LocalToGlobalMapping - AO */
/* ---------------------------------------------------------------- */
PETSC_ENUM(ISType)
PETSC_ENUM_CHECK_RANGE(ISType, IS_GENERAL, IS_BLOCK)
PETSC_ENUM(ISGlobalToLocalMappingType)
PETSC_ENUM_DEFAULT_VALUE(ISGlobalToLocalMappingType, IS_GTOLM_MASK)
PETSC_ENUM_CHECK_RANGE(ISGlobalToLocalMappingType, 
		       IS_GTOLM_MASK,  IS_GTOLM_DROP)
PETSC_ENUM(AOType)
PETSC_ENUM_CHECK_RANGE(AOType,  AO_BASIC, AO_MAPPING)
/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Vec */
/* ---------------------------------------------------------------- */
PETSC_ENUM(VecOption)
PETSC_ENUM_CHECK_RANGE(VecOption,
		       VEC_IGNORE_OFF_PROC_ENTRIES,
		       VEC_TREAT_OFF_PROC_ENTRIES)
#if 0
PETSC_ENUM(VecOperation)
PETSC_ENUM_CHECK_RANGE(VecOperation,
		       VECOP_VIEW, VECOP_LOADINTOVECTOR)
#else
%ignore VecOperation;
#endif
/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Mat */
/* ---------------------------------------------------------------- */
PETSC_ENUM(MatOption)
PETSC_ENUM_CHECK_RANGE(MatOption, 
		       MAT_ROW_ORIENTED, MAT_ERROR_LOWER_TRIANGULAR)
PETSC_ENUM(MatDuplicateOption)
PETSC_ENUM_CHECK_RANGE(MatDuplicateOption,
		       MAT_DO_NOT_COPY_VALUES, MAT_COPY_VALUES)
PETSC_ENUM(MatAssemblyType)
PETSC_ENUM_DEFAULT_VALUE(MatAssemblyType, MAT_FINAL_ASSEMBLY)
PETSC_ENUM_CHECK_RANGE(MatAssemblyType,
		       MAT_FINAL_ASSEMBLY, MAT_FLUSH_ASSEMBLY)
PETSC_ENUM(MatStructure)
PETSC_ENUM_DEFAULT_VALUE(MatStructure, DIFFERENT_NONZERO_PATTERN)
PETSC_ENUM_CHECK_RANGE(MatStructure,
		       SAME_NONZERO_PATTERN, SUBSET_NONZERO_PATTERN)
PETSC_ENUM(MatInfoType)
PETSC_ENUM_CHECK_RANGE(MatInfoType,
		       MAT_LOCAL, MAT_GLOBAL_SUM)
#if 0
PETSC_ENUM(MatOperation)
PETSC_ENUM_CHECK_RANGE(MatOperation,
		       MATOP_SET_VALUES, MATOP_PTAP_NUMERIC_MPIAIJ)
#else
%ignore MatOperation;
#endif
/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* KSP - PC */
/* ---------------------------------------------------------------- */
PETSC_ENUM(KSPNormType);
PETSC_ENUM_CHECK_RANGE(KSPNormType, KSP_NO_NORM, KSP_NATURAL_NORM)
PETSC_OVERRIDE(
PetscErrorCode,
KSPNormTypeString,
(KSPNormType val, const char* norm_type[]), {
  PetscFunctionBegin;
  *norm_type = KSPNormTypes[val];
  PetscFunctionReturn(0);
})

PETSC_ENUM(KSPConvergedReason);
PETSC_OVERRIDE(
PetscErrorCode,
KSPConvergedReasonString,
(KSPConvergedReason val, const char* reason[]), {
  PetscFunctionBegin;
  *reason = KSPConvergedReasons[val];
  PetscFunctionReturn(0);
})

PETSC_ENUM(PCSide)
PETSC_ENUM_DEFAULT_VALUE(PCSide, PC_LEFT)
PETSC_ENUM_CHECK_RANGE(PCSide, PC_LEFT, PC_SYMMETRIC)
PETSC_OVERRIDE(
PetscErrorCode,
PCSideString,
(PCSide val, const char* pc_side[]), {
  PetscFunctionBegin;
  *pc_side = PCSides[val];
  PetscFunctionReturn(0);
})
/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* SNES */
/* ---------------------------------------------------------------- */
PETSC_ENUM(SNESConvergedReason)
PETSC_OVERRIDE(
PetscErrorCode,
SNESConvergedReasonString,
(SNESConvergedReason val, const char* reason[]), {
  PetscFunctionBegin;
  *reason = SNESConvergedReasons[val];
  PetscFunctionReturn(0);
})
/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* TS */
/* ---------------------------------------------------------------- */
PETSC_ENUM(TSProblemType)
PETSC_ENUM_CHECK_RANGE(TSProblemType, TS_LINEAR, TS_NONLINEAR)
/* ---------------------------------------------------------------- */



/*
 * Local Variables:
 * mode: C
 * End:
 */
