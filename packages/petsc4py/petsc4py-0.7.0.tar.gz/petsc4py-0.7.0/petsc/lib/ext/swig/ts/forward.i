
/* TS */
typedef struct _p_TS* TS;

/* TSType */
typedef char* TSType;
#define TS_EULER           "euler"
#define TS_BEULER          "beuler"
#define TS_PSEUDO          "pseudo"
#define TS_CRANK_NICHOLSON "crank-nicholson"
#define TS_SUNDIALS        "sundials"
#define TS_RUNGE_KUTTA     "runge-kutta"

/* TSProblemType */
typedef enum {
  TS_LINEAR,
  TS_NONLINEAR
} TSProblemType;

/*
 * Local Variables:
 * mode: C
 * End:
 */
