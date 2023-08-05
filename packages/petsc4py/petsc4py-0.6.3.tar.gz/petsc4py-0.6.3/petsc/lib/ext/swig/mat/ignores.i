/* ---------------------------------------------------------------- */

%ignore  MAT_FILE_COOKIE;
%ignore  MATSNESMFCTX_COOKIE;
%ignore  MAT_FDCOLORING_COOKIE;
%ignore  MAT_PARTITIONING_COOKIE;

/* ---------------------------------------------------------------- */

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

/* ---------------------------------------------------------------- */

%ignore MatList;
%ignore MatInitializePackage;
%ignore MatRegisterAll;
%ignore MatRegister;
%ignore MatRegisterAllCalled;
%ignore PetscFList;

/* ---------------------------------------------------------------- */

%ignore MatConvertRegister;
%ignore MatConvertRegisterAllCalled;
%ignore MatConvertRegisterDestroy;
%ignore MatConvertList;

/* ---------------------------------------------------------------- */

%ignore MatOptions;

/* ---------------------------------------------------------------- */

%ignore MatISGetLocalMat;
%ignore MatSeqAIJGetInodeSizes;

%ignore MatOrderingRegister;
%ignore MatOrderingRegisterDestroy;
%ignore MatOrderingRegisterAll;
%ignore MatOrderingRegisterAllCalled;
%ignore MatColoringRegisterAllCalled;
%ignore MatOrderingList;

%ignore MatCreateSeqFFTW;
%ignore MatCreateMPIFFTW;

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

/*
 * Local Variables:
 * mode: C
 * End:
 */
