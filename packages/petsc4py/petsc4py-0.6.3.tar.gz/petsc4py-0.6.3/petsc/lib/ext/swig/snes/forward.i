
/* SNES */
typedef struct _p_SNES* SNES;

/* SNESType */
typedef const char* SNESType;
#define SNESLS   "ls"
#define SNESTR   "tr"
#define SNESTEST "test"

/* SNESConvergedReason */
typedef enum {
  /* converged */
  SNES_CONVERGED_FNORM_ABS         =  2,
  SNES_CONVERGED_FNORM_RELATIVE    =  3,
  SNES_CONVERGED_PNORM_RELATIVE    =  4,
  SNES_CONVERGED_TR_DELTA          =  7,
  /* diverged */
  SNES_DIVERGED_FUNCTION_DOMAIN    = -1,  
  SNES_DIVERGED_FUNCTION_COUNT     = -2,  
  SNES_DIVERGED_LINEAR_SOLVE       = -3, 
  SNES_DIVERGED_FNORM_NAN          = -4, 
  SNES_DIVERGED_MAX_IT             = -5,
  SNES_DIVERGED_LS_FAILURE         = -6,
  SNES_DIVERGED_LOCAL_MIN          = -8,
  /* iterating */
  SNES_CONVERGED_ITERATING         =  0
} SNESConvergedReason;

/*
 * Local Variables:
 * mode: C
 * End:
 */
