
/* PC */
typedef struct _p_PC* PC;

/* PCType */
typedef const char* PCType;
#define PCNONE            "none"
#define PCJACOBI          "jacobi"
#define PCSOR             "sor"
#define PCLU              "lu"
#define PCSHELL           "shell"
#define PCBJACOBI         "bjacobi"
#define PCMG              "mg"
#define PCEISENSTAT       "eisenstat"
#define PCILU             "ilu"
#define PCICC             "icc"
#define PCASM             "asm"
#define PCKSP             "ksp"
#define PCCOMPOSITE       "composite"
#define PCREDUNDANT       "redundant"
#define PCSPAI            "spai"
#define PCNN              "nn"
#define PCCHOLESKY        "cholesky"
#define PCSAMG            "samg"
#define PCPBJACOBI        "pbjacobi"
#define PCMAT             "mat"
#define PCHYPRE           "hypre"
#define PCFIELDSPLIT      "fieldsplit"
#define PCTFS             "tfs"
#define PCML              "ml"
#define PCPROMETHEUS      "prometheus"
#define PCGALERKIN        "galerkin"

/* PCSide */
typedef enum { 
  PC_LEFT,
  PC_RIGHT,
  PC_SYMMETRIC
} PCSide;


/*
 * Local Variables:
 * mode: C
 * End:
 */
