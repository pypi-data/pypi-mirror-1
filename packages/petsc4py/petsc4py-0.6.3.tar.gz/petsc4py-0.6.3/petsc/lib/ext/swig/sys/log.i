/* $Id$ */

/* ---------------------------------------------------------------- */

PetscErrorCode PetscLogBegin(void);
PetscErrorCode PetscLogAllBegin(void);

PetscErrorCode PetscLogActions(PetscTruth);
PetscErrorCode PetscLogObjects(PetscTruth);

PetscErrorCode PetscLogPrintSummary(MPI_Comm comm, const char filename[]);
PetscErrorCode PetscLogDump(const char filename[]);

/* ---------------------------------------------------------------- */


%apply int* OUTPUT { int *stage };
%typemap(arginit, noblock=1) int *stage { temp$argnum = 0;}

PetscErrorCode PetscLogStageRegister(int *stage, const char sname[]);
PetscErrorCode PetscLogStagePush(int stage);
PetscErrorCode PetscLogStagePop(void);

%clear int *stage;

PetscErrorCode PetscLogStageSetActive(int stage, PetscTruth isActive);
PetscErrorCode PetscLogStageSetVisible(int stage, PetscTruth isVisible);

/* ---------------------------------------------------------------- */

%apply int* OUTPUT { PetscCookie *cookie };
%typemap(arginit, noblock=1) PetscCookie *cookie { temp$argnum = 0;}
PetscErrorCode PetscLogClassRegister(PetscCookie* cookie,const char name[]);
%clear PetscCookie *cookie;

PetscErrorCode PetscLogEventActivateClass(PetscCookie cookie);
PetscErrorCode PetscLogEventDeactivateClass(PetscCookie cookie);

/* ---------------------------------------------------------------- */


%apply int* OUTPUT { PetscEvent *event };
%typemap(arginit, noblock=1) PetscEvent *event  { temp$argnum = 0;}
%typemap(default, noblock=1) PetscCookie cookie { $1 = PETSC_SMALLEST_COOKIE;}
PetscErrorCode PetscLogEventRegister(PetscEvent *event,const char name[],PetscCookie cookie);
%clear PetscEvent *event;
%clear PetscEvent *event;
%clear PetscCookie cookie;

%typemap(default, noblock=1) 
PetscObject o1, PetscObject o2, PetscObject o3, PetscObject o4 { $1 = PETSC_NULL; }
%typemap(check) 
PetscObject o1, PetscObject o2, PetscObject o3, PetscObject o4 = PetscObject OBJ_OR_NONE;
PetscErrorCode PetscLogEventBegin(PetscEvent event,
				  PetscObject o1, PetscObject o2, 
				  PetscObject o3, PetscObject o4);
PetscErrorCode PetscLogEventEnd(PetscEvent event,
				PetscObject o1, PetscObject o2,
				PetscObject o3, PetscObject o4);
%clear PetscObject o1, PetscObject o2, PetscObject o3, PetscObject o4;

PetscErrorCode PetscLogEventActivate(PetscEvent event);
PetscErrorCode PetscLogEventDeactivate(PetscEvent event);

/* ---------------------------------------------------------------- */

PetscErrorCode PetscLogFlops(PetscLogDouble flops);

/* ---------------------------------------------------------------- */

%apply double* OUTPUT { PetscLogDouble *time }
PetscErrorCode PetscGetTime(PetscLogDouble *time);
PetscErrorCode PetscGetCPUTime(PetscLogDouble *time);
%clear PetscLogDouble *time;
%ignore PetscGetTime;
%ignore PetscGetCPUTime;

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
