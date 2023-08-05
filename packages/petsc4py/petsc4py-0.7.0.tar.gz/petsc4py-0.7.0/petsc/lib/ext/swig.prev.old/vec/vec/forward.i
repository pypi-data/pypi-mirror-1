
/* Vec */
typedef struct _p_Vec* Vec;

/* VecType */
typedef const char* VecType;
#define VECSEQ         "seq"
#define VECMPI         "mpi"
#define VECFETI        "feti"
#define VECSHARED      "shared"
#define VECSIEVE       "sieve"

/* NormType */
typedef enum {
  NORM_1=0,
  NORM_2=1,
  NORM_FROBENIUS=2,
  NORM_INFINITY=3,
  NORM_1_AND_2=4
} NormType;

%constant NORM_MAX = NORM_MAX;

/* VecOption */
typedef enum {
  VEC_IGNORE_OFF_PROC_ENTRIES,
  VEC_TREAT_OFF_PROC_ENTRIES
} VecOption;

typedef struct _p_VecScatter* VecScatter;

/*
 * Local Variables:
 * mode: C
 * End:
 */
