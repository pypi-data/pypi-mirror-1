/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

ARRAY_FLAT(PetscInt n, const PetscInt app[],
	   ARRAY_INPUT, PyPetsc_INT)
ARRAY_RAW(const PetscInt petsc[],
	  ARRAY_INPUT, PyPetsc_INT);

PetscErrorCode
AOCreateBasic(MPI_Comm,
	      PetscInt n, const PetscInt app[], const PetscInt petsc[],
	      AO* CREATE);

PetscErrorCode
AOCreateMapping(MPI_Comm,
		PetscInt n,const PetscInt app[],const PetscInt petsc[],
		AO* CREATE);

%clear (PetscInt n, const PetscInt app[]);
%clear const PetscInt petsc[];

#if 0
%wrapper %{
#define AOCreateBasic(is1,is2,ao)   AOCreateBasicIS((is1),(is2),(ao))
#define AOCreateMapping(is1,is2,ao) AOCreateMappingIS((is1),(is2),(ao))
%}
PetscErrorCode AOCreateBasic(IS,IS OBJ_OR_NONE, AO *CREATE);
PetscErrorCode AOCreateMapping(IS,IS OBJ_OR_NONE, AO *CREATE);
%wrapper %{
#undef AOCreateBasic
#undef AOCreateMapping
%}
#endif

#if 0
%rename (AOCreateBasic)   AOCreateBasicIS;
%rename (AOCreateMapping) AOCreateMappingIS;
#endif

PetscErrorCode AOCreateBasicIS(IS, IS OBJ_OR_NONE, AO* CREATE);
PetscErrorCode AOCreateMappingIS(IS, IS OBJ_OR_NONE, AO* CREATE);


%ignore AOCreateBasic;
%ignore AOCreateMapping;
%ignore AOCreateBasicIS;
%ignore AOCreateMappingIS;

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
/*   */
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

%ignore AOPetscToApplicationIS;
%ignore AOApplicationToPetscIS;
%ignore AOPetscToApplication;
%ignore AOApplicationToPetsc;
%ignore AOPetscToApplicationPermuteInt;
%ignore AOApplicationToPetscPermuteInt;
%ignore AOPetscToApplicationPermuteReal;
%ignore AOApplicationToPetscPermuteReal;

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Ignores                                                          */
/* ---------------------------------------------------------------- */

%ignore AO_PetscToApplication;
%ignore AO_ApplicationToPetsc;
%ignore AORegister_Private;

%ignore DMInitializePackage;

%ignore AODATA_COOKIE;

%ignore AODataType;

%ignore AODataCreateBasic;
%ignore AODataView;
%ignore AODataDestroy;
%ignore AODataLoadBasic;
%ignore AODataGetInfo;

%ignore AODataKeyAdd;
%ignore AODataKeyRemove;

%ignore AODataKeySetLocalToGlobalMapping;
%ignore AODataKeyGetLocalToGlobalMapping;
%ignore AODataKeyRemap;

%ignore AODataKeyExists;
%ignore AODataKeyGetInfo;
%ignore AODataKeyGetOwnershipRange;

%ignore AODataKeyGetNeighbors;
%ignore AODataKeyGetNeighborsIS;
%ignore AODataKeyGetAdjacency;

%ignore AODataKeyGetActive;
%ignore AODataKeyGetActiveIS;
%ignore AODataKeyGetActiveLocal;
%ignore AODataKeyGetActiveLocalIS;

%ignore AODataKeyPartition;

%ignore AODataSegmentAdd;
%ignore AODataSegmentRemove;
%ignore AODataSegmentAddIS;

%ignore AODataSegmentExists;
%ignore AODataSegmentGetInfo;

%ignore AODataSegmentGet;
%ignore AODataSegmentRestore;
%ignore AODataSegmentGetIS;
%ignore AODataSegmentRestoreIS;

%ignore AODataSegmentGetLocal;
%ignore AODataSegmentRestoreLocal;
%ignore AODataSegmentGetLocalIS;
%ignore AODataSegmentRestoreLocalIS;

%ignore AODataSegmentGetReduced;
%ignore AODataSegmentGetReducedIS;
%ignore AODataSegmentGetExtrema;

%ignore AODataSegmentPartition;

%ignore AODataPartitionAndSetupLocal;
%ignore AODataAliasAdd;

%ignore AOData2dGridAddNode;
%ignore AOData2dGridInput;
%ignore AOData2dGridFlipCells;
%ignore AOData2dGridComputeNeighbors;
%ignore AOData2dGridComputeVertexBoundary;
%ignore AOData2dGridDraw;
%ignore AOData2dGridDestroy;
%ignore AOData2dGridCreate;
%ignore AOData2dGridToAOData;

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
