
/* KSP */
typedef struct _p_KSP* KSP;

/* KSPType */
typedef const char* KSPType;
#define KSPRICHARDSON "richardson"
#define KSPCHEBYCHEV  "chebychev"
#define KSPCG         "cg"
#define   KSPCGNE       "cgne"
#define   KSPSTCG       "stcg"
#define KSPGMRES      "gmres"
#define   KSPFGMRES     "fgmres" 
#define   KSPLGMRES     "lgmres"
#define KSPTCQMR      "tcqmr"
#define KSPBCGS       "bcgs"
#define KSPBCGSL      "bcgsl"
#define KSPCGS        "cgs"
#define KSPTFQMR      "tfqmr"
#define KSPCR         "cr"
#define KSPLSQR       "lsqr"
#define KSPPREONLY    "preonly"
#define KSPQCG        "qcg"
#define KSPBICG       "bicg"
#define KSPMINRES     "minres"
#define KSPSYMMLQ     "symmlq"
#define KSPLCD        "lcd"

/* KSPNormType */
typedef enum {
  KSP_NO_NORM = 0,
  KSP_PRECONDITIONED_NORM = 1,
  KSP_UNPRECONDITIONED_NORM = 2,
  KSP_NATURAL_NORM = 3
} KSPNormType;

/* KSPConvergedReason */
typedef enum {
  /* converged */
  KSP_CONVERGED_RTOL               =  2,
  KSP_CONVERGED_ATOL               =  3,
  KSP_CONVERGED_ITS                =  4,
  KSP_CONVERGED_STCG_NEG_CURVE     =  5,
  KSP_CONVERGED_STCG_CONSTRAINED   =  6,
  KSP_CONVERGED_STEP_LENGTH        =  7,
  KSP_CONVERGED_HAPPY_BREAKDOWN    =  8,
  /* diverged */
  KSP_DIVERGED_NULL                = -2,
  KSP_DIVERGED_ITS                 = -3,
  KSP_DIVERGED_DTOL                = -4,
  KSP_DIVERGED_BREAKDOWN           = -5,
  KSP_DIVERGED_BREAKDOWN_BICG      = -6,
  KSP_DIVERGED_NONSYMMETRIC        = -7,
  KSP_DIVERGED_INDEFINITE_PC       = -8,
  KSP_DIVERGED_NAN                 = -9,
  KSP_DIVERGED_INDEFINITE_MAT      = -10,
  /* iterating */
  KSP_CONVERGED_ITERATING          =  0
} KSPConvergedReason;

/*
 * Local Variables:
 * mode: C
 * End:
 */
