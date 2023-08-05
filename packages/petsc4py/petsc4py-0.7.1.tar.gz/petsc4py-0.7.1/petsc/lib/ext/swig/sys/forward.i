
typedef int PetscErrorCode;
typedef int PetscCookie;
typedef int PetscEvent;

typedef int PetscMPIInt;
typedef double PetscLogDouble;

/* PetscObject */
typedef struct _p_PetscObject* PetscObject;

typedef enum { 
  ENUM_DUMMY
} PetscEnum;

typedef enum { 
  PETSC_FALSE,
  PETSC_TRUE 
} PetscTruth;

%constant PETSC_YES = PETSC_YES;
%constant PETSC_NO  = PETSC_NO;

#define PETSC_NULL       0
#define PETSC_DECIDE    -1
#define PETSC_DEFAULT   -2
#define PETSC_IGNORE     PETSC_NULL
#define PETSC_DETERMINE  PETSC_DECIDE

typedef enum {
  FILE_MODE_READ,
  FILE_MODE_WRITE,
  FILE_MODE_APPEND,
  FILE_MODE_UPDATE,
  FILE_MODE_APPEND_UPDATE
} PetscFileMode;

typedef enum {
  NOT_SET_VALUES, 
  INSERT_VALUES, 
  ADD_VALUES, 
  MAX_VALUES
} InsertMode;

typedef enum {
  SCATTER_FORWARD=0, 
  SCATTER_REVERSE=1, 
  SCATTER_FORWARD_LOCAL=2, 
  SCATTER_REVERSE_LOCAL=3, 
  SCATTER_LOCAL=2
} ScatterMode;


/* ---------------------------------------------------------------- */

/* forward declares XXXView() functions to define appropriate typemap
   for PetscViewer argument */

%define %PETSC_OBJECT_VIEW(PETSc_t)
PetscErrorCode 
PETSc_t##View(PETSc_t, PetscViewer OPTIONAL);
%ignore PETSc_t##View;
%enddef

%PETSC_OBJECT_VIEW( PetscObject            )
%PETSC_OBJECT_VIEW( PetscViewer            )
%PETSC_OBJECT_VIEW( PetscRandom            )
%PETSC_OBJECT_VIEW( IS                     )
%PETSC_OBJECT_VIEW( AO                     )
%PETSC_OBJECT_VIEW( ISLocalToGlobalMapping )
%PETSC_OBJECT_VIEW( Vec                    )
%PETSC_OBJECT_VIEW( VecScatter             )
#if 0
%PETSC_OBJECT_VIEW( MatNullSpace           )
#endif
%PETSC_OBJECT_VIEW( Mat                    )
%PETSC_OBJECT_VIEW( KSP                    )
%PETSC_OBJECT_VIEW( PC                     )
%PETSC_OBJECT_VIEW( SNES                   )
%PETSC_OBJECT_VIEW( TS                     )

/* ---------------------------------------------------------------- */

/* PetscViewer */
typedef struct _p_PetscViewer* PetscViewer;

/* PetscViewerType */
typedef const char* PetscViewerType;
#define PETSC_VIEWER_SOCKET       "socket"
#define PETSC_VIEWER_ASCII        "ascii"
#define PETSC_VIEWER_BINARY       "binary"
#define PETSC_VIEWER_STRING       "string"
#define PETSC_VIEWER_DRAW         "draw"
#define PETSC_VIEWER_VU           "vu"
#define PETSC_VIEWER_MATHEMATICA  "mathematica"
#define PETSC_VIEWER_SILO         "silo"
#define PETSC_VIEWER_NETCDF       "netcdf"
#define PETSC_VIEWER_HDF4         "hdf4"
#define PETSC_VIEWER_MATLAB       "matlab"

/* PetscViewerFormat */
typedef enum {
  PETSC_VIEWER_ASCII_DEFAULT,
  PETSC_VIEWER_ASCII_MATLAB,
  PETSC_VIEWER_ASCII_MATHEMATICA,
  PETSC_VIEWER_ASCII_IMPL,
  PETSC_VIEWER_ASCII_INFO,
  PETSC_VIEWER_ASCII_INFO_DETAIL,
  PETSC_VIEWER_ASCII_COMMON,
  PETSC_VIEWER_ASCII_SYMMODU,
  PETSC_VIEWER_ASCII_INDEX,
  PETSC_VIEWER_ASCII_DENSE,
  PETSC_VIEWER_ASCII_VTK,
  PETSC_VIEWER_ASCII_VTK_CELL,
  PETSC_VIEWER_ASCII_VTK_COORDS,
  PETSC_VIEWER_ASCII_PCICE,
  PETSC_VIEWER_ASCII_PYLITH,
  PETSC_VIEWER_ASCII_PYLITH_LOCAL,
  PETSC_VIEWER_BINARY_DEFAULT,
  PETSC_VIEWER_BINARY_NATIVE,
  PETSC_VIEWER_DRAW_BASIC,
  PETSC_VIEWER_DRAW_LG,
  PETSC_VIEWER_DRAW_CONTOUR, 
  PETSC_VIEWER_DRAW_PORTS,
  PETSC_VIEWER_NATIVE,
  PETSC_VIEWER_NOFORMAT,
  PETSC_VIEWER_ASCII_FACTOR_INFO
} PetscViewerFormat;

/* ---------------------------------------------------------------- */

/* forward declares XXXView() functions to define appropriate typemap
   for PetscViewer argument */

%define %PETSC_OBJECT_VIEW(PETSc_t)
PetscErrorCode 
PETSc_t##View(PETSc_t, PetscViewer OPTIONAL);
%ignore PETSc_t##View;
%enddef

%PETSC_OBJECT_VIEW( PetscObject            )
%PETSC_OBJECT_VIEW( PetscViewer            )
%PETSC_OBJECT_VIEW( PetscRandom            )
%PETSC_OBJECT_VIEW( IS                     )
%PETSC_OBJECT_VIEW( AO                     )
%PETSC_OBJECT_VIEW( ISLocalToGlobalMapping )
%PETSC_OBJECT_VIEW( Vec                    )
%PETSC_OBJECT_VIEW( VecScatter             )
#if 0
%PETSC_OBJECT_VIEW( MatNullSpace           )
#endif
%PETSC_OBJECT_VIEW( Mat                    )
%PETSC_OBJECT_VIEW( KSP                    )
%PETSC_OBJECT_VIEW( PC                     )
%PETSC_OBJECT_VIEW( SNES                   )
%PETSC_OBJECT_VIEW( TS                     )

/* ---------------------------------------------------------------- */

typedef struct _p_PetscRandom* PetscRandom;

typedef const char* PetscRandomType;
#define PETSCRAND    "petscrand"
#define PETSCRAND48  "petscrand48"
#define SPRNG        "sprng"          

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
