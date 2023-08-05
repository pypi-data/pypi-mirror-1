/* ---------------------------------------------------------------- */

%ignore ISGetIndices;
%ignore ISRestoreIndices;

%ignore ISBlockGetIndices;
%ignore ISBlockRestoreIndices;

%ignore ISColoringType;
%ignore ISColoringTypes;
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
