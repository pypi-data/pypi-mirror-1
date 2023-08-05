/* $Id$ */

/* ---------------------------------------------------------------- */

/* AO */
typedef struct _p_AO* AO;
/* AOType */
typedef enum {AO_BASIC=0, AO_ADVANCED=1, AO_MAPPING=2} AOType;

/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt n, const PetscInt app[],
	   ARRAY_INPUT, PyPetsc_INT)
ARRAY_RAW(const PetscInt petsc[],
	  ARRAY_INPUT, PyPetsc_INT);

PetscErrorCode AOCreateBasic(MPI_Comm,PetscInt n,const PetscInt app[],const PetscInt petsc[],AO* CREATE);
PetscErrorCode AOCreateMapping(MPI_Comm,PetscInt n,const PetscInt app[],const PetscInt petsc[],AO* CREATE);

%clear (PetscInt n, const PetscInt app[]);
%clear const PetscInt petsc[];

#if 0
%wrapper %{
#define AOCreateBasic(is1,is2,ao)   AOCreateBasicIS((is1),(is2),(ao))
#define AOCreateMapping(is1,is2,ao) AOCreateMappingIS((is1),(is2),(ao))
%}
PetscErrorCode AOCreateBasic(IS,IS OPTIONAL, AO *CREATE);
PetscErrorCode AOCreateMapping(IS,IS OPTIONAL, AO *CREATE);
%wrapper %{
#undef AOCreateBasic
#undef AOCreateMapping
%}
#endif

#if 0
%rename (AOCreateBasic)   AOCreateBasicIS;
%rename (AOCreateMapping) AOCreateMappingIS;
#endif

PetscErrorCode AOCreateBasicIS(IS, IS OPTIONAL, AO* CREATE);
PetscErrorCode AOCreateMappingIS(IS, IS OPTIONAL, AO* CREATE);

PetscErrorCode AOView(AO,PetscViewer);
PetscErrorCode AODestroy(AO);

/* ---------------------------------------------------------------- */
#if 0
%wrapper %{
static PetscErrorCode 
AOGetType(AO ao, const char* type[])
{
  static char *AOTypes[] = {"basic", "advanced", "mapping", "new"};
  PetscFunctionBegin;
  PetscValidHeaderSpecific(ao,AO_COOKIE,1);
  switch(((PetscObject)ao)->type) {
  case AO_BASIC:    *type = AOTypes[0]; break;
  case AO_ADVANCED: *type = AOTypes[1]; break;
  case AO_MAPPING:  *type = AOTypes[2]; break;
  case AO_NEW:      *type = AOTypes[3]; break;
  default:          *type = NULL;       break;
  }
  PetscFunctionReturn(0);
}
%}

static PetscErrorCode AOGetType(AO, const char*[]);
#endif
/* ---------------------------------------------------------------- */

PetscErrorCode AOPetscToApplicationIS(AO, IS);
PetscErrorCode AOApplicationToPetscIS(AO, IS);

%rename (AOPetscToApplication) AOPetscToApplicationIS;
%rename (AOApplicationToPetsc) AOApplicationToPetscIS;
PetscErrorCode AOPetscToApplicationIS(AO, IS);
PetscErrorCode AOApplicationToPetscIS(AO, IS);

ARRAY_FLAT(PetscInt, PetscInt[],  ARRAY_IO, PyPetsc_INT);
ARRAY_FLAT(PetscInt, PetscReal[], ARRAY_IO, PyPetsc_REAL);

PetscErrorCode AOPetscToApplication(AO, PetscInt, PetscInt[]);
PetscErrorCode AOApplicationToPetsc(AO, PetscInt, PetscInt[]);

PetscErrorCode AOPetscToApplicationPermuteInt(AO,  PetscInt, PetscInt[]);
PetscErrorCode AOApplicationToPetscPermuteInt(AO,  PetscInt, PetscInt[]);
PetscErrorCode AOPetscToApplicationPermuteReal(AO, PetscInt, PetscReal[]);
PetscErrorCode AOApplicationToPetscPermuteReal(AO, PetscInt, PetscReal[]);

%clear (PetscInt, PetscInt[]);
%clear (PetscInt, PetscReal[]);

PetscErrorCode AOMappingHasApplicationIndex(AO,PetscInt,PetscTruth*);
PetscErrorCode AOMappingHasPetscIndex(AO,PetscInt,PetscTruth*);

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
