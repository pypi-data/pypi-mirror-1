/* $Id$ */

/* ---------------------------------------------------------------- */
/* Base Python type object for MPI Communicators                    */
/* ---------------------------------------------------------------- */

%header %{

EXTERN_C_BEGIN

typedef struct PyPetscCommObject {
  PyObject_HEAD
  MPI_Comm comm;
} PyPetscCommObject;

static PyTypeObject* Py_PetscComm_Type;

#define PyPetscComm(op) \
        ((PyPetscCommObject*)(op))
#define PyPetscComm_OBJ(op) \
        (PyPetscComm(op)->comm)
#define PyPetscComm_VAL(op) \
        (PyPetscComm(op)->comm)
#define PyPetscComm_PTR(op) \
        (&(PyPetscComm(op)->comm))

static void
comm_dealloc(PyPetscCommObject *self)
{
  PyPetscComm_OBJ(self) = MPI_COMM_NULL;
  self->ob_type->tp_free(self);
}

static PyObject *
comm_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyPetscCommObject *self;
  self = PyPetscComm(type->tp_alloc(type, 0));
  if (self != NULL)  PyPetscComm_OBJ(self) = MPI_COMM_NULL;
  return (PyObject*)self;
}

/* static PyObject * */
/* comm_new(PyTypeObject *type, PyObject *args, PyObject *kwds) */
/* { */
/*   PyPetscCommObject *self; */
/*   PyObject *ob = NULL; */
/*   static char *kwlist[] = {"comm", 0}; */

/*   if (!PyArg_ParseTupleAndKeywords(args, kwds,  */
/* 				   "|O:Comm", kwlist, */
/* 				   &ob)) return NULL; */
  
/*   self = PyPetscComm(type->tp_alloc(type, 0)); */
/*   if (self != NULL)  PyPetscComm_OBJ(self) = MPI_COMM_NULL; */
/*   return (PyObject*)self; */
/* } */


#define comm_alloc PyType_GenericAlloc
#define comm_init  (initproc)0
#define comm_free  PyObject_Del

static PyObject*
comm_repr(PyPetscCommObject *ob) 
{
  MPI_Comm comm = PyPetscComm_OBJ(ob);
  return PyString_FromFormat("<%s object at %p (%p)>",
			     ob->ob_type->tp_name,
			     (void*)ob, (void*)comm);
}

static int
comm_nonzero(PyPetscCommObject *ob)
{
  return (PyPetscComm_OBJ(ob) != MPI_COMM_NULL);
}

static PyNumberMethods comm_number_methods = {
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	(inquiry)comm_nonzero,	/*nb_nonzero*/
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0,
};

#define comm_as_number   (&comm_number_methods)
#define comm_as_sequence (PySequenceMethods*)0
#define comm_as_mapping  (PyMappingMethods*)0

static PyObject *
comm_richcompare(PyPetscCommObject *o1, 
		 PyPetscCommObject *o2, int op)
{
  int      flag;
  PyObject *res;

  /* Make sure both arguments are the same type */
  if (!(PyObject_TypeCheck((PyObject*)o1,
			   Py_PetscComm_Type) &&
	PyObject_TypeCheck((PyObject*)o2,
			   Py_PetscComm_Type))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
  if (op != Py_EQ && op != Py_NE) {
    PyErr_SetString(PyExc_TypeError,
		    "cannot compare MPI communicators "
		    "using <, <=, >, >=");
    return NULL;
  }
  {
    MPI_Comm comm1 = PyPetscComm_OBJ(o1);
    MPI_Comm comm2 = PyPetscComm_OBJ(o2);
    if ((comm1 != MPI_COMM_NULL) &&  (comm2 != MPI_COMM_NULL)) {
      int ierr = MPI_Comm_compare(comm1, comm2, &flag);
      if (ierr != MPI_SUCCESS) {
	PyErr_SetString(PyExc_RuntimeError,
			"error comparing communicators");
	return NULL;
      }
    } else {
      if ((comm1 == MPI_COMM_NULL) &&  (comm2 == MPI_COMM_NULL))
	flag = MPI_IDENT;
      else
	flag = MPI_UNEQUAL;
    }
  }
  
  if ( (op == Py_EQ) == 
       ((flag == MPI_IDENT) || (flag == MPI_CONGRUENT)) )
    res = Py_True;
  else
    res = Py_False;
  
  Py_INCREF(res);
  return res;
}

static PyObject * 
comm_get_this(PyPetscCommObject *self, void *closure) 
{ 
  MPI_Comm *ob = &PyPetscComm_OBJ(self);
  if (*ob != MPI_COMM_NULL) {
    return SWIG_NewPointerObj(SWIG_as_voidptr(ob),
			      SWIGTYPE_p_MPI_Comm, 0);
  }
  Py_RETURN_NONE;
}

static int 
comm_set_this(PyPetscCommObject *self, PyObject *value,
	      void *closure)
{ 
  if (value == NULL) { 
    PyErr_SetString(PyExc_TypeError, "cannot delete attribute");
    return -1;
  } 
  /* ignore, do nothing */
  if (PyErr_Occurred()) return -1;
  return 0; 
}

static PyObject *
comm_get_own(PyPetscCommObject *self, void *closure)
{ 
  Py_XINCREF(Py_False);
  return Py_False;
} 

static int 
comm_set_own(PyPetscCommObject *self, PyObject *value, void *closure) {
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "cannot delete attribute");
    return -1;
  } 
  /* ignore, do nothing */
  if (PyErr_Occurred()) return -1;
  return 0;
}

static PyGetSetDef comm_getset[] = {
  {"this",
   (getter)comm_get_this, (setter)comm_set_this,
   "SWIG pointer object", NULL},
  {"thisown",
   (getter)comm_get_own,  (setter)comm_set_own,
   "SWIG pointer object ownership", NULL},

  {NULL}  /* Sentinel */
};

#define comm_methods 0
#define comm_members 0

PyDoc_STRVAR(comm_doc, "Base type for MPI communicators");

static PyTypeObject _Py_PetscComm_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  0,					/*ob_size*/
  SWIG_name".Comm",			/*tp_name*/
  sizeof(PyPetscCommObject),		/*tp_basicsize*/
  0,					/*tp_itemsize*/

  (destructor)comm_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)0,				/*tp_compare*/
  (reprfunc)comm_repr,			/*tp_repr*/

  comm_as_number,			/*tp_as_number*/
  comm_as_sequence,			/*tp_as_sequence*/
  comm_as_mapping,			/*tp_as_mapping*/

  (hashfunc)0,				/*tp_hash*/
  (ternaryfunc)0,			/*tp_call*/
  (reprfunc)0,				/*tp_str*/
  (getattrofunc)0,			/*tp_getattro*/
  (setattrofunc)0,			/*tp_setattro*/

  (PyBufferProcs*)0,			/*tp_as_buffer*/

  Py_TPFLAGS_DEFAULT  |
  Py_TPFLAGS_BASETYPE,			/*tp_flags*/

  comm_doc, 				/*tp_doc*/

  (traverseproc)0,			/*tp_traverse */

  (inquiry)0,				/*tp_clear */

  (richcmpfunc)comm_richcompare, 	/*tp_richcompare */

  (long)0,				/*tp_weaklistoffset */

  (getiterfunc)0,			/*tp_iter */
  (iternextfunc)0,			/*tp_iternext */

  comm_methods,				/*tp_methods */
  comm_members,				/*tp_members */
  comm_getset,				/*tp_getset */
  0,					/*tp_base */
  0,					/*tp_dict */
  (descrgetfunc)0,			/*tp_descr_get */
  (descrsetfunc)0,			/*tp_descr_set */
  (long)0,				/*tp_dictoffset */

  comm_init,				/*tp_init */
  comm_alloc,				/*tp_alloc */
  comm_new,				/*tp_new */
  comm_free,           			/*tp_free */
};

#undef comm_alloc
#undef comm_init
#undef comm_free

#undef comm_as_number
#undef comm_as_sequence
#undef comm_as_mapping

#undef comm_methods
#undef comm_members

EXTERN_C_END

%}

%init %{
Py_PetscComm_Type = &_Py_PetscComm_Type;
if (PyType_Ready(Py_PetscComm_Type) < 0)  return;
PyModule_AddObject(m, "Comm", (PyObject*)Py_PetscComm_Type);
if(PyErr_Occurred()) return;
PyComm_Type = Py_PetscComm_Type;
%}



/* ---------------------------------------------------------------- */
/* Comm C API                                                       */
/* ---------------------------------------------------------------- */

%header %{
/* pointer to Python type object for Comm */
static PyTypeObject* PyComm_Type = NULL;

/* macros to check the type of Comm objects */
#define PyComm_Check(op) \
        PyObject_TypeCheck(op, PyComm_Type)
#define PyComm_CheckExact(op) \
        ((op)->ob_type == PyComm_Type)

/* extact the underlying MPI_comm, no type checking*/
#define PyComm_VAL(op) PyPetscComm_VAL(op)
#define PyComm_PTR(op) PyPetscComm_PTR(op)

%}

#if 0
%{
/* extact the underlying PETSc PETSc_t, does type checking */
static MPI_Comm
PyComm_AsVal(PyObject* op) {
  if(!PyComm_Check(op)) {
    PyErr_SetString(PyExc_TypeError, "expecting a 'Comm' object");
    return MPI_COMM_NULL;
  }
  return PyComm_VAL(op);
}
static MPI_Comm*
PyComm_AsPtr(PyObject* op) {
  if(!PyComm_Check(op)) {
    PyErr_SetString(PyExc_TypeError, "expecting a 'Comm' object");
    return NULL;
  }
  return PyComm_PTR(op);
}
%}
#endif


/* ---------------------------------------------------------------- */


/* ---------------------------------------------------------------- */
/* Factory functions, MPI_Comm -> Python object                   */
/* ---------------------------------------------------------------- */

%header %{
static PyObject*
PyComm_New(MPI_Comm obj)
{
  PyTypeObject* type;
  PyObject*     self;
  /* check object type */
  if ((type = PyComm_Type) == NULL) {
    PyErr_SetString(PyExc_RuntimeError, 
		    "type object for 'MPI_Comm' not registered");
    return NULL;
  }
  /* allocate a new object */
  self = (PyObject*) type->tp_alloc(type, 0);
  /* fill attributes of allocated object */
  if (self != NULL) PyPetscComm_OBJ(self) = obj;
  /* return new object */
  return self;
}
%}

/* ---------------------------------------------------------------- */



/* ---------------------------------------------------------------- */
/* Type registration                                                */
/* ---------------------------------------------------------------- */

%wrapper %{
static PyObject* 
CommTypeRegister(PyObject* type) {
  if (PyComm_Type == NULL || PyComm_Type == Py_PetscComm_Type) {
    if (!PyType_Check(type)) {
      PyErr_SetString(PyExc_RuntimeError, "expecting a type object");
      return NULL;
    }
    PyComm_Type = (PyTypeObject*) type;
  } else {
    PyErr_SetString(PyExc_RuntimeError, "type already registered");
    return NULL;
  }
  Py_RETURN_NONE;
}
%}

static PyObject* CommTypeRegister(PyObject* type);

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
