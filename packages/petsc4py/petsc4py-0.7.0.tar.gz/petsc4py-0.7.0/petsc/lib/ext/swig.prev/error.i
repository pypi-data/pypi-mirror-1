/* $Id$ */

%include exception.i

/* error management macros */
%header %{
#undef  SETERRQ
#define SETERRQ(n, s) \
   {return PetscError(__LINE__,__FUNCT__,__FILE__,__SDIR__,n,1,s);}

#undef  SETERRQ1
#define SETERRQ1(n,s,a1) \
   {return PetscError(__LINE__,__FUNCT__,__FILE__,__SDIR__,n,1,s,a1);}

#undef  SETERRQ2
#define SETERRQ2(n,s,a1,a2) \
   {return PetscError(__LINE__,__FUNCT__,__FILE__,__SDIR__,n,1,s,a1,a2);}

#undef  SETERRQ3
#define SETERRQ3(n,s,a1,a2,a3) \
   {return PetscError(__LINE__,__FUNCT__,__FILE__,__SDIR__,n,1,s,a1,a2,a3);}

#undef  CHKERRQ
#define CHKERRQ(n) \
   if (n) {return PetscError(__LINE__,__FUNCT__,__FILE__,__SDIR__,n,0," ");}

%}

/* --------------- */
/* Exception class */
/* --------------- */

%header %{
static PyObject* _PyExc_PetscError = NULL;
%}

%wrapper %{
EXTERN_C_BEGIN
static PyObject*
PetscSetExceptionClass(PyObject* exc)
{
  if (!exc) {
    PyErr_SetString(_PyExc_PetscError, "null pointer"); 
    return NULL;
  }
  Py_INCREF(exc);
  Py_XDECREF(_PyExc_PetscError);
  _PyExc_PetscError = exc;
  Py_RETURN_NONE;
}
EXTERN_C_END
%}

%init %{
_PyExc_PetscError = PyErr_NewException(SWIG_name".Error",PyExc_RuntimeError,NULL);
if (PyErr_Occurred()) return;
%}

static PyObject* PetscSetExceptionClass(PyObject*);


/* ----------------------- */
/* TraceBack Error Handler */
/* ----------------------- */

%header %{
static PyObject* PyPetscTraceBackError = NULL;
%}

%wrapper %{
EXTERN_C_BEGIN
static PetscErrorCode
PyPetscTraceBackErrorHandler
(int line, const char *fun, const char* file, const char *dir,
 PetscErrorCode n, int p, const char *mess, void *ctx) {

  PyObject      *list  = (PyObject*) ctx;
  PyObject      *pytxt = NULL;

  PetscFunctionBegin;
  
  pytxt = PyString_FromFormat("%s() line %d in %s%s",
			      fun, line, dir, file);
  if (pytxt) PyList_Insert(list, 0, pytxt);
  Py_XDECREF(pytxt);

  if (p==1) { /* the error originated here */
    PyList_SetSlice(list, 1, PyList_GET_SIZE(list), NULL);
    if (n == PETSC_ERR_MEM) {
      PetscLogDouble mem,rss;
      PetscMallocGetCurrentUsage(&mem);
      PetscMemoryGetCurrentUsage(&rss);
      pytxt = PyString_FromFormat("Out of memory. "
				  "Allocated: %d, "
				  "Used by process: %d",
				  (int)mem,(int)rss);
      if (pytxt) {
	PyList_Append(list, pytxt); 
	Py_DECREF(pytxt);
      }
    } else {
      const char *text  = NULL;
      PetscErrorMessage(n, &text, PETSC_NULL);
      if (text)  {
	pytxt = PyString_FromString(text);
	if (pytxt) PyList_Append(list, pytxt); 
	Py_XDECREF(pytxt);
      }
    }
    if (mess)  {
      pytxt = PyString_FromString(mess);
      if (pytxt) PyList_Append(list, pytxt);
      Py_XDECREF(pytxt);
    }
  }

  PetscFunctionReturn(n);
}
EXTERN_C_END
%}

%init %{
PyPetscTraceBackError = PyList_New(0);
if (PyErr_Occurred()) return;
PyModule_AddObject(m, "PetscTraceBackError", PyPetscTraceBackError);
if (PyErr_Occurred()) return;
%}



/* -------------------- */
/* PETSc error handling */
/* -------------------- */

%header %{
EXTERN_C_BEGIN
static void 
PyErr_SetPetscError(PetscErrorCode ierr)
{
  PyObject* exc_type; 
  PyObject* exc_value; 
  PyObject* exc_traceback;
  PyErr_Fetch(&exc_type, &exc_value, &exc_traceback);
  if (!exc_type) {
    Py_XINCREF(_PyExc_PetscError);
    exc_type = _PyExc_PetscError;
  }
  if (!exc_value) {
    const char* txt; char* spc;
    PetscErrorMessage(ierr, &txt, &spc);
    exc_value = Py_BuildValue("(iss)", (int)ierr, txt, spc);
  }
  PyErr_Restore(exc_type, exc_value, exc_traceback);
}
EXTERN_C_END
%}

%header %{
#define PETSC_seterrmess(mess)           \
do {                                     \
  char *basemess;                        \
  PetscErrorMessage(0, NULL, &basemess); \
  PetscStrncpy(basemess, (mess), 1023);  \
} while(0)

#define PETSC_seterrcode(ierr)                          \
do {                                                    \
  if (ierr) { PyErr_SetPetscError((ierr)); SWIG_fail; } \
} while(0)

#define PETSC_seterr(ierr, mess)                  \
do {                                              \
  PETSC_seterrmess(mess); PETSC_seterrcode(ierr); \
} while(0)
%}


%header %{
#define PETSC_chkerr(ierr) \
do { \
  if ((ierr)) { PyErr_SetPetscError((ierr)); SWIG_fail; } \
} while(0)
%}

%typemap(out, noblock=1) PetscErrorCode
{PETSC_chkerr($1); %set_output(VOID_Object);}


%header %{
#define PETSC_chkptr(obj) \
do { \
  if ((obj) == PETSC_NULL) \
    PETSC_seterr(PETSC_ERR_ARG_NULL,"null pointer to object"); \
  if ((unsigned long)(obj) & (unsigned long)3) \
    PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"invalid pointer to object"); \
} while (0)

#define PETSC_chkheader(obj) \
do { \
  if (((PetscObject)(obj))->cookie == PETSCFREEDHEADER) \
    PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"object already freed"); \
  if (((PetscObject)(obj))->cookie < PETSC_SMALLEST_COOKIE || \
      ((PetscObject)(obj))->cookie > PETSC_LARGEST_COOKIE) \
    PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"object already freed or wrong type of object"); \
} while (0)

#define PETSC_chkcookie(obj, COOKIE) \
do { \
  if (((PetscObject)(obj))->cookie != (COOKIE)) {	  \
    if (((PetscObject)(obj))->cookie == PETSCFREEDHEADER) \
      PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"object already freed"); \
    else \
      PETSC_seterr(PETSC_ERR_ARG_WRONG,"object already freed or wrong type of object"); \
  } \
} while (0)

EXTERN_C_BEGIN
SWIGINTERNINLINE int
_PETSC_chkobj(PetscObject obj, PetscCookie cookie) {
  PETSC_chkptr(obj); /* check pointer */
  if (cookie == PETSC_OBJECT_COOKIE)
    PETSC_chkheader(obj);         /* base type */
  else
    PETSC_chkcookie(obj, cookie); /* derived types */
  return 1;
 fail:
  return 0;
}
EXTERN_C_END

#define PETSC_chkobj(o,c) _PETSC_chkobj((PetscObject)(o),(c))
%}


/*
 * Local Variables:
 * mode: C
 * End:
 */
