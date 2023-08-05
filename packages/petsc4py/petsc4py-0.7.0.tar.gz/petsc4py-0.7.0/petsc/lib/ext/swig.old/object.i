/* $Id$ */

/* ---------------------------------------------------------------- */
/* Creation Functions                                               */
/* ---------------------------------------------------------------- */

PetscErrorCode
PetscObjectCreate(MPI_Comm comm, PetscObject* CREATE);

PETSC_OVERRIDE(
PetscErrorCode,
PetscObjectDestroy, (PetscObject* INPUT), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidPointer(INPUT,1);
  ierr = PetscObjectDestroy(*INPUT); CHKERRQ(ierr);
  *INPUT = PETSC_NULL;
  PetscFunctionReturn(0);
})

%ignore PetscObjectCreate;

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
PetscObjectDispose, (PetscObject* INPUT), {
  PetscFunctionBegin;
  PetscValidPointer(INPUT,1);
  *INPUT = PETSC_NULL;
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

PetscErrorCode
PetscObjectExists(PetscObject OBJ_OR_NONE, PetscTruth*);

%ignore PetscObjectExists;

/* ---------------------------------------------------------------- */

%apply const char** { const char* obj_name[] };
%apply const char** { const char* type_name[] };
%apply const char** { const char* class_name[] };

PetscErrorCode
PetscObjectGetName(PetscObject, const char* obj_name[]);
%ignore PetscObjectGetName;

PETSC_OVERRIDE(
PetscErrorCode,
PetscObjectGetClassName,
(PetscObject obj, const char* class_name[]), {
  PetscFunctionBegin;
  PetscValidHeader(obj,1);
  PetscValidPointer(class_name,2);
  if (!obj) SETERRQ(PETSC_ERR_ARG_CORRUPT,"Null object");
  *class_name = obj->class_name;
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscObjectGetType,
(PetscObject obj, PetscInt* type, const char* type_name[]), {
  PetscFunctionBegin;
  PetscValidHeader(obj,1);
  PetscValidPointer(type_name,2);
  PetscValidIntPointer(type,3);
  if (!obj) SETERRQ(PETSC_ERR_ARG_CORRUPT,"Null object");
  *type_name = obj->type_name;
  *type      = obj->type;
  PetscFunctionReturn(0);
})

%clear const char* obj_name[];
%clear const char* type_name[];
%clear const char* class_name[];

/* ---------------------------------------------------------------- */

PETSC_OVERRIDE(
PetscErrorCode,
PetscObjectGetState,
(PetscObject obj, PetscInt* state), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeader(obj,1);
  ierr = PetscObjectStateQuery(obj, state); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode,
PetscObjectSetState,
(PetscObject obj, PetscInt state), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeader(obj,1);
  ierr = PetscObjectSetState(obj, state); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode, 
PetscObjectStateIncrease,
(PetscObject obj), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeader(obj,1);
  ierr = PetscObjectStateIncrease(obj); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

PETSC_OVERRIDE(
PetscErrorCode, 
PetscObjectStateDecrease,
(PetscObject obj), {
  PetscErrorCode ierr;
  PetscFunctionBegin;
  PetscValidHeader(obj,1);
  ierr = PetscObjectStateDecrease(obj); CHKERRQ(ierr);
  PetscFunctionReturn(0);
})

/* ---------------------------------------------------------------- */

%apply PetscObject OBJ_OR_NONE { PetscObject ptr }
PetscErrorCode
PetscObjectCompose(PetscObject obj,
		   const char name[],
		   PetscObject ptr);
%clear PetscObject ptr;

%apply PetscObject* NEWREF { PetscObject *ptr }
PetscErrorCode
PetscObjectQuery(PetscObject obj,
		 const char name[],
		 PetscObject *ptr);
%clear PetscObject *ptr;

%ignore PetscObjectCompose;
%ignore PetscObjectQuery;

/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* Ignores */
/* ---------------------------------------------------------------- */

%ignore PetscObjectQueryFunction;
%ignore PetscObjectComposeFunction;
%ignore PetscObjectPublish;
%ignore PetscObjectChangeTypeName;
%ignore PetscObjectRegisterDestroy;
%ignore PetscObjectRegisterDestroyAll;

%ignore PetscObjectContainerCreate;
%ignore PetscObjectContainerDestroy;
%ignore PetscObjectContainerSetUserDestroy;
%ignore PetscObjectContainerGetPointer;
%ignore PetscObjectContainerSetPointer;

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
