
/* Mat */
typedef struct _p_Mat* Mat;

/* MatType */
typedef const char* MatType;
#define MATSAME            "same"
#define MATSEQMAIJ         "seqmaij"
#define MATMPIMAIJ         "mpimaij"
#define MATMAIJ            "maij"
#define MATIS              "is"
#define MATMPIROWBS        "mpirowbs"
#define MATSEQAIJ          "seqaij"
#define MATMPIAIJ          "mpiaij"
#define MATAIJ             "aij"
#define MATSHELL           "shell"
#define MATSEQBDIAG        "seqbdiag"
#define MATMPIBDIAG        "mpibdiag"
#define MATBDIAG           "bdiag"
#define MATSEQDENSE        "seqdense"
#define MATMPIDENSE        "mpidense"
#define MATDENSE           "dense"
#define MATSEQBAIJ         "seqbaij"
#define MATMPIBAIJ         "mpibaij"
#define MATBAIJ            "baij"
#define MATMPIADJ          "mpiadj"
#define MATSEQSBAIJ        "seqsbaij"
#define MATMPISBAIJ        "mpisbaij"
#define MATSBAIJ           "sbaij"
#define MATDAAD            "daad"
#define MATMFFD            "mffd"
#define MATNORMAL          "normal"
#define MATLRC             "lrc"
#define MATSEQAIJSPOOLES   "seqaijspooles"
#define MATMPIAIJSPOOLES   "mpiaijspooles"
#define MATSEQSBAIJSPOOLES "seqsbaijspooles"
#define MATMPISBAIJSPOOLES "mpisbaijspooles"
#define MATAIJSPOOLES      "aijspooles"
#define MATSBAIJSPOOLES    "sbaijspooles"
#define MATSUPERLU         "superlu"
#define MATSUPERLU_DIST    "superlu_dist"
#define MATUMFPACK         "umfpack"
#define MATESSL            "essl"
#define MATLUSOL           "lusol"
#define MATAIJMUMPS        "aijmumps"
#define MATSBAIJMUMPS      "sbaijmumps"
#define MATDSCPACK         "dscpack"
#define MATMATLAB          "matlab"
#define MATSEQCSRPERM      "seqcsrperm"
#define MATMPICSRPERM      "mpicsrperm"
#define MATCSRPERM         "csrperm"
#define MATSEQCRL          "seqcrl"
#define MATMPICRL          "mpicrl"
#define MATCRL             "crl"
#define MATPLAPACK         "plapack"
#define MATSCATTER         "scatter"

/* MatReuse */
typedef enum {
  MAT_INITIAL_MATRIX,
  MAT_REUSE_MATRIX
} MatReuse;

/* MatAssemblyType */
typedef enum {
  MAT_FLUSH_ASSEMBLY=1,
  MAT_FINAL_ASSEMBLY=0
} MatAssemblyType;

/* MatDuplicateOption */
typedef enum {
  MAT_DO_NOT_COPY_VALUES,
  MAT_COPY_VALUES
} MatDuplicateOption;

/* MatInfoType */
typedef enum {
  MAT_LOCAL=1,
  MAT_GLOBAL_MAX=2,
  MAT_GLOBAL_SUM=3
} MatInfoType;

/* MatStructure */
typedef enum {
  SAME_NONZERO_PATTERN,
  DIFFERENT_NONZERO_PATTERN,
  SAME_PRECONDITIONER,
  SUBSET_NONZERO_PATTERN
} MatStructure;

/* MatOrderingType */
typedef char* MatOrderingType;
#define MATORDERING_NATURAL     "natural"
#define MATORDERING_ND          "nd"
#define MATORDERING_1WD         "1wd"
#define MATORDERING_RCM         "rcm"
#define MATORDERING_QMD         "qmd"
#define MATORDERING_ROWLENGTH   "rowlength"
#define MATORDERING_DSC_ND      "dsc_nd"
#define MATORDERING_DSC_MMD     "dsc_mmd"
#define MATORDERING_DSC_MDF     "dsc_mdf"
#define MATORDERING_CONSTRAINED "constrained"
#define MATORDERING_IDENTITY    "identity"
#define MATORDERING_REVERSE     "reverse"

%constant MatOrderingType MATORDERING_OWD = MATORDERING_1WD;

/* MatOption */
typedef enum {
  MAT_ROW_ORIENTED=1,MAT_COLUMN_ORIENTED=2,MAT_ROWS_SORTED=4,
  MAT_COLUMNS_SORTED=8,MAT_NO_NEW_NONZERO_LOCATIONS=16,
  MAT_YES_NEW_NONZERO_LOCATIONS=32,MAT_SYMMETRIC=64,
  MAT_STRUCTURALLY_SYMMETRIC=65,MAT_NO_NEW_DIAGONALS=66,
  MAT_YES_NEW_DIAGONALS=67,MAT_INODE_LIMIT_1=68,MAT_INODE_LIMIT_2=69,
  MAT_INODE_LIMIT_3=70,MAT_INODE_LIMIT_4=71,MAT_INODE_LIMIT_5=72,
  MAT_IGNORE_OFF_PROC_ENTRIES=73,MAT_ROWS_UNSORTED=74,
  MAT_COLUMNS_UNSORTED=75,MAT_NEW_NONZERO_LOCATION_ERR=76,
  MAT_NEW_NONZERO_ALLOCATION_ERR=77,MAT_USE_HASH_TABLE=78,
  MAT_KEEP_ZEROED_ROWS=79,MAT_IGNORE_ZERO_ENTRIES=80,MAT_USE_INODES=81,
  MAT_DO_NOT_USE_INODES=82,MAT_NOT_SYMMETRIC=83,MAT_HERMITIAN=84,
  MAT_NOT_STRUCTURALLY_SYMMETRIC=85,MAT_NOT_HERMITIAN=86,
  MAT_SYMMETRY_ETERNAL=87,MAT_NOT_SYMMETRY_ETERNAL=88,
  MAT_USE_COMPRESSEDROW=89,MAT_DO_NOT_USE_COMPRESSEDROW=90,
  MAT_IGNORE_LOWER_TRIANGULAR=91,MAT_ERROR_LOWER_TRIANGULAR=92,MAT_GETROW_UPPERTRIANGULAR=93
} MatOption;

/* MatNullSpace */
typedef struct _p_MatNullSpace* MatNullSpace;


/*
 * Local Variables:
 * mode: C
 * End:
 */
