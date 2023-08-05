/* $Id$ */

/* ---------------------------------------------------------------- */
/* Base Python type object for all PETSc objects                    */
/* ---------------------------------------------------------------- */

%header %{
EXTERN_C_BEGIN

typedef struct PyPetscObjectObject {
  PyObject_HEAD
  PetscObject obj;
  PyObject*   own;
  PyObject*   swig;
} PyPetscObjectObject;

static PyTypeObject* Py_PetscObject_Type;

#define PyPetscObject(op) \
        ((PyPetscObjectObject*)(op))
#define PyPetscObject_OBJ(op) \
        (PyPetscObject(op)->obj)
#define PyPetscObject_OWN(op) \
        (PyPetscObject(op)->own)
#define PyPetscObject_OWNOBJ(op) \
        ((PyPetscObject(op)->own) == Py_True)
#define PyPetscObject_SWIG(op) \
        (PyPetscObject(op)->swig)
#define PyPetscObject_SWIGTHIS(op) \
        (PyPetscObject(op)->swig)

SWIGINTERNINLINE int
_obj_valid(PetscObject obj)
{
  return (obj != PETSC_NULL &&
	  obj->cookie >= PETSC_SMALLEST_COOKIE &&
	  obj->cookie <= PETSC_LARGEST_COOKIE);
}

SWIGINTERNINLINE void
_obj_clean(PyPetscObjectObject *self)
{
  self->obj = PETSC_NULL; /* force pointer to null */
  self->own = Py_True;    /* force ownership to true */
  Py_XDECREF(self->swig);
  self->swig = NULL;
}

SWIGINTERNINLINE PetscErrorCode
_obj_destroy(PetscObject obj) 
{
  if (_obj_valid(obj) && obj->bops->destroy)
    if (!PetscFinalizeCalled)
      return PetscObjectDestroy(obj);
  return 0;
}

static void
obj_dealloc(PyPetscObjectObject *self)
{
  if (self->own == Py_True &&  _obj_destroy(self->obj) != 0)
    PyErr_Format(PyExc_RuntimeError,
		 "destroying a %s object",
		 self->ob_type->tp_name);
  _obj_clean(self);
  self->ob_type->tp_free(self);
}

static PyObject *
obj_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyPetscObjectObject *self;
  self = (PyPetscObjectObject*) type->tp_alloc(type, 0);
  if (self != NULL)  {
    self->obj  = PETSC_NULL;
    self->own  = Py_True;
    self->swig = NULL;
  }
  return (PyObject*)self;
}

#define obj_alloc PyType_GenericAlloc
#define obj_init  (initproc)0
#define obj_free  PyObject_Del

static PyObject*
obj_repr(PyPetscObjectObject *self) 
{
  if (!_obj_valid(self->obj)) _obj_clean(self); /*@*/
  return PyString_FromFormat("<%s object at %p (%p)>",
			     self->ob_type->tp_name,
			     (void*)self, (void*)self->obj);
}

static int
obj_nonzero(PyPetscObjectObject *ob)
{
  if (!_obj_valid(ob->obj)) _obj_clean(ob); /*@*/
  return ob->obj != PETSC_NULL;
}

static PyNumberMethods obj_number_methods = {
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	(inquiry)obj_nonzero,	/*nb_nonzero*/
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0,
};

#define obj_as_number   (&obj_number_methods)
#define obj_as_sequence (PySequenceMethods*)0
#define obj_as_mapping  (PyMappingMethods*)0

static PyObject *
obj_richcompare(PyPetscObjectObject *o1, 
		PyPetscObjectObject *o2, int op)
{
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyObject_TypeCheck((PyObject*)o1,
			   Py_PetscObject_Type) &&
	PyObject_TypeCheck((PyObject*)o2,
			   Py_PetscObject_Type))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }

  if (!_obj_valid(o1->obj)) _obj_clean(o1); /*@*/
  if (!_obj_valid(o2->obj)) _obj_clean(o2); /*@*/

  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare PETSc objects "
		    "using <, <=, >, >=");
    return NULL;
  }
  
  if ((op == Py_EQ) == 
      (PyPetscObject_OBJ(o1) == PyPetscObject_OBJ(o2)))
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}

static PyObject * 
obj_get_this(PyPetscObjectObject *self, void *closure) 
{ 
  if (!_obj_valid(self->obj)) _obj_clean(self); /*@*/
  if (self->obj == PETSC_NULL) Py_RETURN_NONE;
  if (self->swig != NULL) {
    PySwigObject *sobj = (PySwigObject*)self->swig;
    if (self->obj != (PetscObject)sobj->ptr) {
      Py_DECREF(self->swig); self->swig = NULL;
    }
  }
  if (self->swig == NULL) {
    PyObject *_getter,*_this;
    _getter = PyObject_GetAttrString((PyObject*)self->ob_type,"__swig_this__");
    if (_getter == NULL) { PyErr_Clear(); Py_RETURN_NONE; }
    _this = PyObject_CallFunction(_getter, "O", (PyObject*)self);
    Py_DECREF(_getter);
    if (_this == NULL) return NULL;
    self->swig = _this;
  }
  Py_INCREF(self->swig);
  return self->swig;
}

static int 
obj_set_this(PyPetscObjectObject *self, PyObject *value,
	     void *closure)
{ 
  if (value == NULL) { 
    PyErr_SetString(PyExc_TypeError, "cannot delete attribute");
    return -1;
  } 
  if (!_obj_valid(self->obj)) _obj_clean(self); /*@*/
  /* ignore, do nothing */
  if (PyErr_Occurred()) return -1;
  return 0; 
}

static PyObject *
obj_get_own(PyPetscObjectObject *self, void *closure)
{ 
  if (!_obj_valid(self->obj)) _obj_clean(self); /*@*/
  Py_XINCREF(self->own);
  return self->own;
} 

static int 
obj_set_own(PyPetscObjectObject *self, PyObject *value, void *closure) {
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "cannot delete attribute");
    return -1;
  } 
  if (!_obj_valid(self->obj)) _obj_clean(self); /*@*/
  if (self->obj != PETSC_NULL) {
    int truth;
    if ((truth = PyObject_IsTrue(value)) == -1) return -1;
    self->own = truth ? Py_True : Py_False;
  }
  return 0;
}

static PyGetSetDef obj_getset[] = {
  {"owner",
   (getter)obj_get_own,  (setter)obj_set_own,
   "PETSc object ownership", NULL},

  {"this",
   (getter)obj_get_this, (setter)obj_set_this,
   "SWIG pointer object", NULL},
  {"thisown",
   (getter)obj_get_own,  (setter)obj_set_own,
   "SWIG pointer object ownership", NULL},

  {NULL}  /* Sentinel */
};

#define obj_methods 0
#define obj_members 0

PyDoc_STRVAR(obj_doc, "Base type for PETSc objects");

static PyTypeObject _Py_PetscObject_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  0,					/*ob_size*/
  SWIG_name".Object",			/*tp_name*/
  sizeof(PyPetscObjectObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)obj_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)obj_repr,			/*tp_repr*/

  obj_as_number,			/*tp_as_number*/
  obj_as_sequence,			/*tp_as_sequence*/
  obj_as_mapping,			/*tp_as_mapping*/

  (hashfunc)0,				/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  (Py_TPFLAGS_DEFAULT  |
   Py_TPFLAGS_BASETYPE |
   Py_TPFLAGS_CHECKTYPES),		/*tp_flags*/

  obj_doc, 				/*tp_doc*/

  (traverseproc)0,			/*tp_traverse */

  (inquiry)0,				/*tp_clear */

  (richcmpfunc)obj_richcompare, 	/*tp_richcompare */

  (long)0,				/*tp_weaklistoffset */

  (getiterfunc)0,			/*tp_iter */
  (iternextfunc)0,			/*tp_iternext */

  obj_methods,				/*tp_methods */
  obj_members,				/*tp_members */
  obj_getset,				/*tp_getset */
  0,					/*tp_base */
  0,					/*tp_dict */
  (descrgetfunc)0,			/*tp_descr_get */
  (descrsetfunc)0,			/*tp_descr_set */
  (long)0,				/*tp_dictoffset */

  obj_init,				/*tp_init */
  obj_alloc,				/*tp_alloc */
  obj_new,				/*tp_new */
  obj_free,           			/*tp_free */
};

#undef obj_alloc
#undef obj_init
#undef obj_free

#undef obj_as_number
#undef obj_as_sequence
#undef obj_as_mapping

#undef obj_methods
#undef obj_members

EXTERN_C_END
%}

%init %{
Py_PetscObject_Type = &_Py_PetscObject_Type;
if (PyType_Ready(Py_PetscObject_Type) < 0)  return;
/* Py_INCREF(Py_PetscObject_Type); */
PyModule_AddObject(m, "Object", (PyObject*)Py_PetscObject_Type);
if(PyErr_Occurred()) return;
%}


/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* C API                                                            */
/* ---------------------------------------------------------------- */

%header %{

#define PY_PETSC_OBJASVAL(PYTYPE, CTYPE)               \
EXTERN_C_BEGIN 					       \
static CTYPE 					       \
Py##CTYPE##_AsVal(PyObject* op) { 		       \
  CTYPE obj;                                           \
  if(!Py##CTYPE##_Check(op)) { 			       \
    PyErr_SetString(PyExc_TypeError, 		       \
                    "expecting a '"#PYTYPE"' object"); \
    return PETSC_NULL; 				       \
  } 						       \
  obj = Py##CTYPE##_VAL(op); 			       \
  if (_obj_valid((PetscObject)obj)) return obj;      \
  _obj_clean(PyPetscObject(op));                       \
  return PETSC_NULL;                                   \
} 						       \
EXTERN_C_END					       

#define PY_PETSC_OBJASPTR(PYTYPE, CTYPE)               \
EXTERN_C_BEGIN 					       \
static CTYPE* 					       \
Py##CTYPE##_AsPtr(PyObject* op) { 		       \
  CTYPE* ptr;                                          \
  if(!Py##CTYPE##_Check(op)) { 			       \
    PyErr_SetString(PyExc_TypeError, 		       \
		    "expecting a "#PYTYPE" object");   \
    return NULL;				       \
  } 						       \
  ptr = Py##CTYPE##_PTR(op); 			       \
  if (!_obj_valid((PetscObject)*ptr))                \
    _obj_clean(PyPetscObject(op));                     \
  return ptr;                                          \
} 						       \
EXTERN_C_END					       

#define PY_PETSC_TYPEREG(PYTYPE, CTYPE)                \
EXTERN_C_BEGIN					       \
static PyObject* 				       \
PYTYPE##TypeRegister(PyObject* type) {		       \
  if (Py##CTYPE##_Type == NULL) {		       \
    if (!PyType_Check(type)) {			       \
      PyErr_SetString(PyExc_RuntimeError, 	       \
		      "expecting a type object");      \
      return NULL;				       \
    }						       \
    Py##CTYPE##_Type = (PyTypeObject*) type;	       \
  } else {					       \
    PyErr_SetString(PyExc_RuntimeError,                \
		    "type already registered");	       \
    return NULL;				       \
  }						       \
  Py_RETURN_NONE;				       \
}						       \
EXTERN_C_END

%}
	
					       
%define %PETSC_OBJECT_TYPE(PYTYPE, CTYPE)

%header %{

/* Python type object for PYTYPE */
static PyTypeObject* Py##CTYPE##_Type = NULL;
PY_PETSC_TYPEREG(PYTYPE, CTYPE)

/* macros to check the type of PYTYPE objects */
#define Py##CTYPE##_Check(op) \
        PyObject_TypeCheck(op, Py##CTYPE##_Type)
#define Py##CTYPE##_CheckExact(op) \
        ((op)->ob_type == Py##CTYPE##_Type)

/* macros to extact the underlying CTYPE, no type checking*/
#define Py##CTYPE##_VAL(op) ((CTYPE)   PyPetscObject_OBJ(op))
#define Py##CTYPE##_PTR(op) ((CTYPE *)&PyPetscObject_OBJ(op))

/* functs to extact the underlying CTYPE, does type checking */
PY_PETSC_OBJASVAL(PYTYPE, CTYPE)
PY_PETSC_OBJASPTR(PYTYPE, CTYPE)
%}

static PyObject* PYTYPE##TypeRegister(PyObject*);

%enddef


%PETSC_OBJECT_TYPE(Object   , PetscObject           )
%PETSC_OBJECT_TYPE(Viewer   , PetscViewer           )
%PETSC_OBJECT_TYPE(Random   , PetscRandom           )
%PETSC_OBJECT_TYPE(IS       , IS                    )
%PETSC_OBJECT_TYPE(AO       , AO                    )
%PETSC_OBJECT_TYPE(LGMapping, ISLocalToGlobalMapping)
%PETSC_OBJECT_TYPE(Vec      , Vec                   )
%PETSC_OBJECT_TYPE(Scatter  , VecScatter            )
%PETSC_OBJECT_TYPE(Mat      , Mat                   )
%PETSC_OBJECT_TYPE(NullSpace, MatNullSpace          )
%PETSC_OBJECT_TYPE(KSP      , KSP                   )
%PETSC_OBJECT_TYPE(PC       , PC                    )
%PETSC_OBJECT_TYPE(SNES     , SNES                  )
%PETSC_OBJECT_TYPE(TS       , TS                    )

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Factory functions, PetscObject -> Python object                  */
/* ---------------------------------------------------------------- */

%header %{
#define PY_PETSC_OBJFACTORY(PYTYPE, CTYPE)                          \
EXTERN_C_BEGIN                                                      \
SWIGINTERN PyObject*                                                \
Py##CTYPE##_New(CTYPE obj)                                          \
{                                                                   \
  PyTypeObject* type;                                               \
  PyObject*     self;                                               \
  /* check object type */                                           \
  if ((type = Py##CTYPE##_Type) == NULL) {                          \
    PyErr_SetString(PyExc_RuntimeError,                             \
		    "type object for "#CTYPE" not registered");     \
    return NULL;                                                    \
  }                                                                 \
  /* allocate a new object */                                       \
  self = (PyObject*) type->tp_alloc(type, 0);                       \
  /* fill attributes of allocated object */                         \
  if (self != NULL) {                                               \
    PyPetscObject_OBJ(self)  = (PetscObject) obj;                   \
    PyPetscObject_OWN(self)  = Py_True;                             \
    PyPetscObject_SWIG(self) = NULL;                                \
  }                                                                 \
  return self;                                                      \
}                                                                   \
EXTERN_C_END                                                        \
EXTERN_C_BEGIN 							    \
SWIGINTERN PyObject* 						    \
Py##CTYPE##_Ref(CTYPE obj) 					    \
{ 								    \
  PyTypeObject* type; 						    \
  PyObject*     self; 						    \
  /* check object type */ 					    \
  if ((type = Py##CTYPE##_Type) == NULL) { 			    \
    PyErr_SetString(PyExc_RuntimeError,  			    \
		    "type object for "#CTYPE" not registered");     \
    return NULL; 						    \
  } 								    \
  /* allocate a new  object */ 					    \
  self = (PyObject*) type->tp_alloc(type, 0); 			    \
  /* fill allocated object */ 					    \
  if (self != NULL) { 						    \
    PyPetscObject_OBJ(self)  = (PetscObject) obj;                   \
    PyPetscObject_OWN(self)  = Py_False;                            \
    PyPetscObject_SWIG(self) = NULL;                                \
  } 								    \
  return self; 							    \
} 								    \
EXTERN_C_END                                                        \
%}

%define %PETSC_OBJFACTORY(PYTYPE, CTYPE)
%header %{PY_PETSC_OBJFACTORY(PYTYPE, CTYPE)%}
%enddef

%PETSC_OBJFACTORY( Object    , PetscObject            )
%PETSC_OBJFACTORY( Viewer    , PetscViewer            )
%PETSC_OBJFACTORY( Random    , PetscRandom            )
%PETSC_OBJFACTORY( IS        , IS                     )
%PETSC_OBJFACTORY( LGMapping , ISLocalToGlobalMapping )
%PETSC_OBJFACTORY( AO        , AO                     )
%PETSC_OBJFACTORY( Vec       , Vec                    )
%PETSC_OBJFACTORY( Scatter   , VecScatter             )
%PETSC_OBJFACTORY( Mat       , Mat                    )
%PETSC_OBJFACTORY( NullSpace , MatNullSpace           )
%PETSC_OBJFACTORY( KSP       , KSP                    )
%PETSC_OBJFACTORY( PC        , PC                     )
%PETSC_OBJFACTORY( SNES      , SNES                   )
%PETSC_OBJFACTORY( TS        , TS                     )



/* ---------------------------------------------------------------- */
/* SWIG pointer and clientdata code                                 */
/* ---------------------------------------------------------------- */

/* This function returns a new SWIG pointer object
   without calling clientdata code */

#if 0
%header %{
SWIGRUNTIME PyObject *
SWIG_NewPointerObj_Petsc(void *ptr, swig_type_info *type, int flags) {
  if (!ptr) {
    return SWIG_Py_Void();
  } else {
    int own = (flags & SWIG_POINTER_OWN) ? SWIG_POINTER_OWN : 0;
    PyObject *robj = PySwigObject_New(ptr, type, 0);
    return robj;
  }
}
%}
#else
%header %{
#define SWIG_NewPointerObj_Petsc SWIG_NewPointerObj
%}
#endif

%wrapper %{
#define PY_PETSC_SWIG_REGISTER(PYTYPE, CTYPE)                  \
EXTERN_C_BEGIN                                                 \
static PyObject*                                               \
PYTYPE##SwigRegister(PyObject *obj) {                          \
  if (!PyCallable_Check(obj)) {                                \
    PyErr_SetString(PyExc_TypeError, "object is not callabe"); \
    return NULL;                                               \
  }                                                            \
  SWIG_TypeClientData(SWIGTYPE_p__p_##CTYPE, obj);             \
  Py_RETURN_NONE;                                              \
}                                                              \
EXTERN_C_END 

#define PY_PETSC_FROM_SWIG(PYTYPE, CTYPE)  \
static PyObject*                           \
PYTYPE##FromSwig(PyObject *obj) {          \
  CTYPE ptr;                               \
  SWIG_ConvertPtr(obj, (void **)&ptr,      \
		  SWIGTYPE_p__p_##CTYPE,   \
		  SWIG_POINTER_EXCEPTION); \
  return Py##CTYPE##_Ref(ptr);             \
}                                          \
EXTERN_C_END
%}


%define %PETSC_SWIGREGISTER(PYTYPE, CTYPE)
/* SWIG pointer getter */
%wrapper %{
#define PYTYPE##__swig_this__(obj, ptr)    \
        do {                               \
	  *ptr = Py##CTYPE##_AsVal(obj);   \
	  if (PyErr_Occurred()) SWIG_fail; \
	} while(0)
%}

%typemap(in) CTYPE SWIGTHIS = SWIGTYPE&;
%typemap(in, numinputs=0) CTYPE* SWIGTHIS
($*ltype temp = PETSC_NULL) "$1 = &temp;";
%typemap(argout, noblock=1)  CTYPE* SWIGTHIS {
  Py_XDECREF($result); if (PyErr_Occurred()) SWIG_fail;
  %set_output(SWIG_NewPointerObj_Petsc(%as_voidptr(*$1),
				       $descriptor(CTYPE),
				       %newpointer_flags));
}
static void PYTYPE##__swig_this__(PyObject*, CTYPE* SWIGTHIS);
%clear CTYPE SWIGTHIS, CTYPE* SWIGTHIS;

#if 0
/* SWIG cliendata */
%wrapper %{
PY_PETSC_SWIG_REGISTER(PYTYPE, CTYPE)
PY_PETSC_FROM_SWIG(PYTYPE, CTYPE)
%}
static PyObject* PYTYPE##SwigRegister(PyObject *obj);
static PyObject* PYTYPE##FromSwig(PyObject *obj);
#endif

%enddef

%PETSC_SWIGREGISTER(Object   , PetscObject           )
%PETSC_SWIGREGISTER(Viewer   , PetscViewer           )
%PETSC_SWIGREGISTER(Random   , PetscRandom           )
%PETSC_SWIGREGISTER(IS       , IS                    )
%PETSC_SWIGREGISTER(AO       , AO                    )
%PETSC_SWIGREGISTER(LGMapping, ISLocalToGlobalMapping)
%PETSC_SWIGREGISTER(Vec      , Vec                   )
%PETSC_SWIGREGISTER(Scatter  , VecScatter            )
%PETSC_SWIGREGISTER(Mat      , Mat                   )
%PETSC_SWIGREGISTER(NullSpace, MatNullSpace          )
%PETSC_SWIGREGISTER(KSP      , KSP                   )
%PETSC_SWIGREGISTER(PC       , PC                    )
%PETSC_SWIGREGISTER(SNES     , SNES                  )
%PETSC_SWIGREGISTER(TS       , TS                    )

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
