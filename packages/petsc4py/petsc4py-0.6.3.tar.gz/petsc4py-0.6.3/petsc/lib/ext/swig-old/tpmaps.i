/* $Id$ */

/* ---------------------------------------------------------------- */
/* SWIG Pointer getter hack                                         */
/* ---------------------------------------------------------------- */

%header %{
SWIGINTERNINLINE PyObject* 
SWIG_getattr_this(PyObject* obj) {
  if (!obj) return NULL;
  obj = PyObject_GetAttr(obj, SWIG_This());
  if (!obj) PyErr_Clear();
  return obj;
}
SWIGINTERNINLINE int
SWIG_convert_ptr(PyObject *obj, void **ptr, swig_type_info *ty, int flags) {
  int res = SWIG_ConvertPtr(obj, ptr, ty, flags);
  if (!SWIG_IsOK(res)) {
    PyObject* _this = SWIG_getattr_this(obj);
    res = SWIG_ConvertPtr(_this, ptr, ty, flags);
    Py_XDECREF(_this);
  }
  return res;
}
#undef  SWIG_ConvertPtr
#define SWIG_ConvertPtr(obj, pptr, type, flags) \
        SWIG_convert_ptr(obj, pptr, type, flags)
%}


/* ---------------------------------------------------------------- */
/* PyObject                                                         */
/* ---------------------------------------------------------------- */

%typemap(in, numinputs=0, noblock=1) 
PyObject **OUTPUT 
($*ltype temp = NULL)
{$1 = &temp;}

%typemap(argout, noblock=1) 
PyObject **OUTPUT 
{ %append_output((PyObject *)(*$1)); }

/* ---------------------------------------------------------------- */
/* MPI Communicators                                                */
/* ---------------------------------------------------------------- */
/* - If a communicator argument is None, PETSC_COMM_WORLD is used.  */
/* - Pointer arguments in functions default to output.              */
/* ---------------------------------------------------------------- */

%typemap(arginit, noblock=1) MPI_Comm 
{ $1 = PETSC_COMM_WORLD; }

%typemap(in, noblock=1) MPI_Comm (void *argp = 0, int res = 0)
{
  if ($input == Py_None) {
    $1 = PETSC_COMM_WORLD;
  } else if (PyComm_Check($input)) {
    $1 = PyComm_VAL($input);
  } else {
    res = SWIG_ConvertPtr($input, &argp, $&descriptor, %convertptr_flags);
    if (!SWIG_IsOK(res))
      %argument_fail(res, "$type", $symname, $argnum); 
    if (!argp) {
      %argument_nullref($type, $symname, $argnum);
    } else {
      $1 = *(%reinterpret_cast(argp, $&ltype));
    }
  }
}

%typemap(check, noblock=1) MPI_Comm
{ 
  if ($1 == MPI_COMM_NULL) PETSC_seterr(PETSC_ERR_ARG_WRONG, "null cummunicator");
}

%typemap(freearg) MPI_Comm "";

%typemap(in, noblock=1) MPI_Comm* INPUT 
(void *argp = 0, int res = 0)
{
  if (PyComm_Check($input)) {
    $1 = PyComm_PTR($input);
  } else {
    res = SWIG_ConvertPtr($input, &argp, $descriptor, %convertptr_flags);
    if (!SWIG_IsOK(res)) {
      %argument_fail(res, "$type", $symname, $argnum); 
    }
  $1 = %reinterpret_cast(argp, $ltype);
  }
}

%typemap(check, noblock=1) MPI_Comm* INPUT
{ 
  if (!$1 || *$1 == MPI_COMM_NULL)
    PETSC_seterr(PETSC_ERR_ARG_WRONG, "null cummunicator");
}

%typemap(argout) MPI_Comm* INPUT "";



%typemap(in, numinputs=0, noblock=1) MPI_Comm* OUTPUT
($*ltype temp = MPI_COMM_NULL) { $1 = &temp; }
%typemap(argout, noblock=1) MPI_Comm* OUTPUT 
{ %append_output(PyComm_New(*$1)); }


%apply MPI_Comm* OUTPUT { MPI_Comm* }



/* ---------------------------------------------------------------- */
/* PETSc Objects                                                    */
/* ---------------------------------------------------------------- */

%{
#define PETSC_chkptr(obj) \
  {if ((obj) == PETSC_NULL) \
     PETSC_seterr(PETSC_ERR_ARG_NULL,"null pointer to object"); \
   if ((unsigned long)(obj) & (unsigned long)3) \
     PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"invalid pointer to object");}

#define PETSC_chkheader(obj) \
  {if (((PetscObject)(obj))->cookie == PETSCFREEDHEADER) \
     PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"object already freed"); \
   if (((PetscObject)(obj))->cookie < PETSC_SMALLEST_COOKIE || \
       ((PetscObject)(obj))->cookie > PETSC_LARGEST_COOKIE) \
     PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"object already freed or wrong type of object");}

#define PETSC_chkcookie(obj, COOKIE) \
  if (((PetscObject)(obj))->cookie != COOKIE) { \
    if (((PetscObject)(obj))->cookie == PETSCFREEDHEADER) \
      PETSC_seterr(PETSC_ERR_ARG_CORRUPT,"object already freed"); \
    else \
      PETSC_seterr(PETSC_ERR_ARG_WRONG,"object already freed or wrong type of object"); }

EXTERN_C_BEGIN
SWIGINTERNINLINE int
_PETSC_chkobj(PetscObject obj, PetscCookie cookie) {
  PETSC_chkptr(obj) /* check pointer */
  if (cookie == PETSC_OBJECT_COOKIE)
    PETSC_chkheader(obj)         /* base type */
  else
    PETSC_chkcookie(obj, cookie) /* derived types */
  return 1;
 fail:
  return 0;
}
EXTERN_C_END

#define PETSC_chkobj(o,c) _PETSC_chkobj((PetscObject)(o),(c))
%}


%define %PETSC_OBJECT_TYPEMAPS(PETSc_t, COOKIE)
%ignore COOKIE; /* ignore cookies */

/* C type */
/* ------ */
%types(PETSc_t);

/* typecheck */
/* --------- */
%typemap(typecheck, precedence=SWIG_TYPECHECK_POINTER, noblock=1) PETSc_t
{ $1 = Py##PETSc_t##_Check($input); }

/* value input */
/* ----------- */
%typemap(in, noblock=1) PETSc_t
{
  $1 = Py##PETSc_t##_AsVal($input);
  if (PyErr_Occurred()) %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
}
%typemap(check, noblock=1) PETSc_t
{
  if (!PETSC_chkobj($1, COOKIE)) SWIG_fail;
}

%typemap(typecheck, precedence=SWIG_TYPECHECK_POINTER, noblock=1) PETSC_t OBJ_OR_NONE
{ $1 = ($input == Py_None) || Py##PETSc_t##_Check($input) ; }

%typemap(arginit)       PETSC_t OBJ_OR_NONE "$1 = PETSC_NULL;";
%typemap(in, noblock=1) PETSc_t OBJ_OR_NONE
{
  if ($input != Py_None) {
    $1 = Py##PETSc_t##_AsVal($input);
    if (PyErr_Occurred()) %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  }
}
%typemap(check, noblock=1)  PETSc_t OBJ_OR_NONE
{
  if ($1 && !PETSC_chkobj($1, COOKIE)) SWIG_fail;
}


/* pointer input */
/* ------------- */
%typemap(typecheck)     PETSc_t* INPUT = PETSc_t;
%typemap(in, noblock=1) PETSc_t* INPUT 
{
  $1 = Py##PETSc_t##_AsPtr($input);
  if (PyErr_Occurred()) %argument_fail(SWIG_TypeError, "$*type", $symname, $argnum);
}
%typemap(check, noblock=1) PETSc_t* INPUT 
{
  if ($1 && !PETSC_chkobj(*$1, COOKIE)) SWIG_fail;
}

/* pointer input-output */
/* -------------------- */
%typemap(typecheck)         PETSc_t* INOUT = PETSc_t* INPUT;
%typemap(in)                PETSc_t* INOUT = PETSc_t* INPUT;
%typemap(check)             PETSc_t* INOUT = PETSc_t* INPUT;
%typemap(argout, noblock=1) PETSc_t* INOUT 
{
  Py_XDECREF(PyPetscObject_SWIGTHIS($input));
  PyPetscObject_SWIGTHIS($input) = NULL;
}



/* for factory functions XXXCreate() */
%typemap(typecheck)     PETSc_t* CREATE = PETSc_t;
%typemap(in, noblock=1) PETSc_t* CREATE
($*ltype auxobj = PETSC_NULL)
{
  if ($input == Py_None) {
    $1 = &auxobj;
  } else {
    $1 = Py##PETSc_t##_AsPtr($input);
    if (!$1) %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
    auxobj = *$1;
  }
}
%typemap(argout)   PETSc_t* CREATE
{
  PyObject* robj;
  if ($input == Py_None) {
    robj = Py##PETSc_t##_##New(auxobj$argnum);
  } else {
    if (PyPetscObject_OWNOBJ($input) &&
	_obj_destroy((PetscObject)auxobj$argnum) != 0)
      PyErr_Warn(PyExc_RuntimeWarning, "trying to destroy a PETSc_t object");
    Py_XDECREF(PyPetscObject_SWIGTHIS($input));
    PyPetscObject_SWIGTHIS($input) = NULL;
    PyPetscObject_OWN($input) = Py_True;
    Py_INCREF($input);
    robj = $input;
  }
  %append_output(robj);
}

/* pointer output */
/* -------------- */
%typemap(in,numinputs=0) PETSc_t* NEWOBJ
($*ltype temp = PETSC_NULL) "$1 = &temp;";
%typemap(argout, noblock=1) PETSc_t* NEWOBJ
{ %append_output(Py##PETSc_t##_##New(*$1)); }

%typemap(in,numinputs=0) PETSc_t* NEWREF
($*ltype temp = PETSC_NULL) "$1 = &temp;";
%typemap(argout, noblock=1) PETSc_t* NEWREF
{ %append_output(Py##PETSc_t##_##Ref(*$1)); }


/* return value   */
/* -------------- */
%typemap(out, noblock=1) PETSc_t OBJNEW {
  if (!PETSC_chkobj($1, COOKIE)) SWIG_fail;
  %set_output(Py##PETSc_t##_##New($1)); 
}
%typemap(out, noblock=1) PETSc_t OBJREF {
  if (!PETSC_chkobj($1, COOKIE)) SWIG_fail;
  PetscObjectReference((PetscObject)$1);
  %set_output(Py##PETSc_t##_##New($1));
}

%enddef

/* ---------------------------------------------------------------- */

%PETSC_OBJECT_TYPEMAPS(PetscObject           , PETSC_OBJECT_COOKIE )
%PETSC_OBJECT_TYPEMAPS(PetscViewer           , PETSC_VIEWER_COOKIE )
%PETSC_OBJECT_TYPEMAPS(PetscRandom           , PETSC_RANDOM_COOKIE )
%PETSC_OBJECT_TYPEMAPS(IS                    , IS_COOKIE           )
%PETSC_OBJECT_TYPEMAPS(AO                    , AO_COOKIE           )
%PETSC_OBJECT_TYPEMAPS(ISLocalToGlobalMapping, IS_LTOGM_COOKIE     )
%PETSC_OBJECT_TYPEMAPS(Vec                   , VEC_COOKIE          )
%PETSC_OBJECT_TYPEMAPS(VecScatter            , VEC_SCATTER_COOKIE  )
%PETSC_OBJECT_TYPEMAPS(MatNullSpace          , MAT_NULLSPACE_COOKIE)
%PETSC_OBJECT_TYPEMAPS(Mat                   , MAT_COOKIE          )
%PETSC_OBJECT_TYPEMAPS(KSP                   , KSP_COOKIE          )
%PETSC_OBJECT_TYPEMAPS(PC                    , PC_COOKIE           )
%PETSC_OBJECT_TYPEMAPS(SNES                  , SNES_COOKIE         )
%PETSC_OBJECT_TYPEMAPS(TS                    , TS_COOKIE           )

/* ---------------------------------------------------------------- */

%typemap(in) Mat* REUSE ($*ltype temp = PETSC_NULL)
{
  $1 = &temp;
  if($input != Py_None) {
    $1 = PyMat_AsPtr($input);
    if (PyErr_Occurred())
      %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  }
}
%typemap(check, noblock=1) Mat* REUSE
{
  if (*$1 && !PETSC_chkobj(*$1, MAT_COOKIE)) SWIG_fail;
}
%typemap(argout) Mat* REUSE
{
  PyObject* mat;
  if ($1 == (&temp$argnum)) {
    mat = PyMat_New(*$1);
    if (PyErr_Occurred()) {
      PetscTruth flg;
      MatValid(*$1, &flg);
      if (flg) MatDestroy(*$1);
      %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
    }
  }  else {
    mat = $input; Py_INCREF(mat);
  }
  %append_output(mat);
}

%ignore MatReuse;

/* ---------------------------------------------------------------- */

/* Array of objects*/

%typemap(arginit) (PetscInt, PetscObject INPUT[]) "$1=0; $2=NULL;";
%typemap(in) (PetscInt, PetscObject INPUT[]) (PyObject* seq = NULL)
{
  PetscInt i;
  PyObject*  pyobj;
  if ($input != Py_None) 
    seq = PySequence_Fast($input,"argument must be sequence");
  else
    seq = PyTuple_New(0);
  if (PyErr_Occurred())
    %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  $1 = PySequence_Fast_GET_SIZE(seq);
  $2 = PyMem_New($*2_ltype, $1);
  if(!$2) SWIG_exception(SWIG_MemoryError,"");
  for (i=0; i<$1; i++) {
    pyobj = PySequence_Fast_GET_ITEM(seq, (Py_ssize_t)i);
    if(!PyPetscObject_Check(pyobj))
      %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
    $2[i] = ($*2_ltype) PyPetscObject_OBJ(pyobj);
  }
}
%typemap(freearg, noblock=1) (PetscInt, PetscObject INPUT[])
"PyMem_Del($2); Py_XDECREF(seq$argnum);";


/* ---------------------------------------------------------------- */

/* output strings */
#if 1
%typemap(in, numinputs=0) const char** ($*ltype temp) "$1 = &temp;";
%typemap(argout) const char** {
  PyObject* o = PyString_FromString(($1 && *$1)?(*$1):"");
  if (PyErr_Occurred())
    %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  %append_output(o);
}
#else
%typemap(in, numinputs=0) 
const char** ($*ltype temp = NULL) "$1 = &temp;";
%typemap(argout) 
const char** {
  PyObject* o;
  if (*$1 != NULL) { 
    o = PyString_FromString(*$1); 
    if (PyErr_Occurred())
      %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  }
  else { 
    o = Py_None; Py_INCREF(Py_None); 
  }
  %append_output(o);
}
#endif

%apply const char** { const char*[] };
%apply const char** {       char*[] };
%apply const char** {       char**  };

/* ---------------------------------------------------------------- */




/* ---------------------------------------------------------------- */
/* PETSc Numeric Types and Precisions */
/* ---------------------------------------------------------------- */

%fragment(SWIG_From_frag(long double),"header",
          fragment=SWIG_From_frag(double)) {
SWIGINTERN SWIG_Object
SWIG_From_dec(long double)(long double v) {
  return SWIG_From(double)((double)v);
}
}
%fragment(SWIG_AsVal_frag(long double),"header",
          fragment=SWIG_AsVal_frag(double)) {
SWIGINTERN int
SWIG_AsVal_dec(long double)(SWIG_Object obj, long double *val) {
  double v;
  int res = SWIG_AsVal(double)(obj, &v);
  if (SWIG_IsOK(res)) {
    if (val) *val = %numeric_cast(v, long double);
  }
  return res;
}
}


/* ---------------------------------------------------------------- */
/* PETSc Enumerations                                               */
/* ---------------------------------------------------------------- */

%types(PetscEnum);

%fragment(SWIG_From_frag(PetscEnum),"header",
          fragment=SWIG_From_frag(int)) {
#define SWIG_From_PetscEnum(e) SWIG_From_int((int)(e))
}
%fragment(SWIG_AsVal_frag(PetscEnum),"header",
          fragment=SWIG_AsVal_frag(int)) {
#define SWIG_AsVal_PetscEnum(o, v)  SWIG_AsVal_int((o), (int*)(v))
}


/* ---------------------------------------------------------------- */
/* PetscInt                                                         */
/* ---------------------------------------------------------------- */

%types(PetscInt);

%fragment(SWIG_From_frag(PetscInt),"header",
          fragment=SWIG_From_frag(long long),
          fragment=SWIG_From_frag(int))
{
%#if defined(PETSC_USE_64BIT_INDICES)
%define_as(SWIG_From(PetscInt), SWIG_From(long long))
%#else
%define_as(SWIG_From(PetscInt), SWIG_From(int))
%#endif
}

%fragment(SWIG_AsVal_frag(PetscInt),"header",
          fragment=SWIG_AsVal_frag(long long),
          fragment=SWIG_AsVal_frag(int))
{
%#if defined(PETSC_USE_64BIT_INDICES)
%define_as(SWIG_AsVal(PetscInt), SWIG_AsVal(long long))
%#else
%define_as(SWIG_AsVal(PetscInt), SWIG_AsVal(int))
%#endif
}


/* ---------------------------------------------------------------- */
/* PetscReal                                                        */
/* ---------------------------------------------------------------- */

%types(PetscReal);

%fragment(SWIG_From_frag(PetscReal),"header",
          fragment=SWIG_From_frag(long double),
          fragment=SWIG_From_frag(double),
          fragment=SWIG_From_frag(float),
	  fragment=SWIG_From_frag(int))
{
%#if   defined(PETSC_USE_SINGLE)
%define_as(SWIG_From(PetscReal), SWIG_From(float))
%#elif defined(PETSC_USE_LONG_DOUBLE)
%define_as(SWIG_From(PetscReal), SWIG_From(long double))
%#elif defined(PETSC_USE_INT)
%define_as(SWIG_From(PetscReal), SWIG_From(int))
%#else
%define_as(SWIG_From(PetscReal), SWIG_From(double))
%#endif
}

%fragment(SWIG_AsVal_frag(PetscReal),"header",
          fragment=SWIG_AsVal_frag(long double),
          fragment=SWIG_AsVal_frag(double),
          fragment=SWIG_AsVal_frag(float),
	  fragment=SWIG_AsVal_frag(int))
{
%#if   defined(PETSC_USE_SINGLE)
%define_as(SWIG_AsVal(PetscReal),  SWIG_AsVal(float))
%#elif defined(PETSC_USE_LONG_DOUBLE)
%define_as(SWIG_AsVal(PetscReal),  SWIG_AsVal(long double))
%#elif defined(PETSC_USE_INT)
%define_as(SWIG_AsVal(PetscReal),  SWIG_AsVal(int))
%#else
%define_as(SWIG_AsVal(PetscReal),  SWIG_AsVal(double))
%#endif
}

/* ---------------------------------------------------------------- */
/* PetscComplex                                                     */
/* ---------------------------------------------------------------- */

%types(PetscComplex);

%include complex.i

%fragment(SWIG_From_frag(PetscComplex),"header",
#ifdef __cplusplus
          fragment=SWIG_From_frag(std::complex<double>))
#else
          fragment=SWIG_From_frag(double complex))
#endif
{
%#if defined(PETSC_CLANGUAGE_CXX)
%define_as(SWIG_From(PetscComplex), SWIG_From(std::complex<double>))
%#else
%define_as(SWIG_From(PetscComplex), SWIG_From(double complex))
%#endif
}

%fragment(SWIG_AsVal_frag(PetscComplex),"header",
#ifdef __cplusplus
          fragment=SWIG_AsVal_frag(std::complex<double>))
#else
          fragment=SWIG_AsVal_frag(double complex))
#endif
{
%#if defined(PETSC_CLANGUAGE_CXX)
%define_as(SWIG_AsVal(PetscComplex), SWIG_AsVal(std::complex<double>))
%#else
%define_as(SWIG_AsVal(PetscComplex), SWIG_AsVal(double complex))
%#endif
}


/* ---------------------------------------------------------------- */
/* PetscScalar                                                      */
/* ---------------------------------------------------------------- */

%types(PetscScalar);

%fragment(SWIG_From_frag(PetscScalar), "header",
          fragment=SWIG_From_frag(PetscReal),
          fragment=SWIG_From_frag(PetscComplex))
{
%#if defined(PETSC_USE_COMPLEX)
%define_as(SWIG_From(PetscScalar), SWIG_From(PetscComplex))
%#else
%define_as(SWIG_From(PetscScalar), SWIG_From(PetscReal))
%#endif
}

%fragment(SWIG_AsVal_frag(PetscScalar), "header",
          fragment=SWIG_AsVal_frag(PetscReal),
          fragment=SWIG_AsVal_frag(PetscComplex))
{
%#if defined(PETSC_USE_COMPLEX)
%define_as(SWIG_AsVal(PetscScalar), SWIG_AsVal(PetscComplex))
%#else
%define_as(SWIG_AsVal(PetscScalar), SWIG_AsVal(PetscReal))
%#endif
}

/* ---------------------------------------------------------------- */
/* Number typemaps                                                  */
/* ---------------------------------------------------------------- */


%define SWIG_TYPECHECK_PETSC_ENUM    SWIG_TYPECHECK_INT32   %enddef
%define SWIG_TYPECHECK_PETSC_INT     SWIG_TYPECHECK_INT32   %enddef
%define SWIG_TYPECHECK_PETSC_REAL    SWIG_TYPECHECK_DOUBLE  %enddef
%define SWIG_TYPECHECK_PETSC_SCALAR  SWIG_TYPECHECK_CPLXDBL %enddef

%define %petsc_value_output_typemap(from_meth, from_frag, Type)
%typemap(in, numinputs=0, noblock=1) 
Type*, Type* OUTPUT ($*ltype temp) { 
  $1 = &temp;
}
%typemap(argout,noblock=1,fragment=from_frag) 
Type*, Type* OUTPUT {
  %append_output(from_meth((*$1)));
}
%enddef


%define %typemaps_petsc(Code, Type...)
%typemaps_primitive(%checkcode(Code), Type);
%petsc_value_output_typemap(SWIG_From(Type),SWIG_From_frag(Type),Type)
%apply Type* INPUT { Type const* }
%typemap(argout) Type const* "";
%apply Type* OUTPUT { Type* }
%enddef


%typemaps_petsc(INT32,        int);
%typemaps_petsc(INT64,        long);
%typemaps_petsc(PETSC_ENUM,   PetscEnum);
%typemaps_petsc(PETSC_INT,    PetscInt);
%typemaps_petsc(PETSC_REAL,   PetscReal);
%typemaps_petsc(PETSC_SCALAR, PetscScalar);


/* ---------------------------------------------------------------- */
/* - If argument is None, enumeration can have default values.      */
/* - Enumerations can be checked for out-of-range values.           */
/* - Pointer arguments in functions default to output.              */
/* ---------------------------------------------------------------- */

%define PETSC_ENUM(EnumType)
%types(EnumType);
%apply PetscEnum         { EnumType         }
%apply PetscEnum*        { EnumType*        }
%apply PetscEnum* INPUT  { EnumType* INPUT  }
%apply PetscEnum* OUTPUT { EnumType* OUTPUT }
%apply PetscEnum* INOUT  { EnumType* INOUT  }
%enddef /* PETSC_ENUM */

%define PETSC_ENUM_DEFAULT_VALUE(EnumType, DEFAULT_ENUM_VALUE)
%typemap(arginit, noblock=1) EnumType
{ $1 = DEFAULT_ENUM_VALUE; }
%typemap(in,noblock=1,fragment=SWIG_AsVal_frag(PetscEnum))
 EnumType ($ltype val, int ecode = 0)
{
  if ($input!=Py_None) {
    ecode = SWIG_AsVal(PetscEnum)($input, &val);
    if (!SWIG_IsOK(ecode)) {
      %argument_fail(ecode, "$ltype", $symname, $argnum);
    } 
    $1 = %static_cast(val,$ltype);
  }
}
%enddef /* PETSC_ENUM_DEFAULT_VALUE */

%define PETSC_ENUM_CHECK_RANGE(EnumType, FIRST_VALUE, LAST_VALUE)
%typemap(check, noblock=1) EnumType {
  if (((int)$1 < (int)FIRST_VALUE) || ((int)$1 > (int)LAST_VALUE))
    PETSC_seterr(PETSC_ERR_ARG_OUTOFRANGE, "invalid value for 'EnumType'");
}
%enddef /* PETSC_ENUM_CHECK_RANGE */


%ignore PetscDataType;
%ignore PetscDataTypes;

%ignore PetscDataTypeToMPIDataType;
%ignore PetscDataTypeGetSize;
%ignore PetscDataTypeGetName;


/*
 * Local Variables:
 * mode: C
 * End:
 */
