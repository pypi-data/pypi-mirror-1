/* $Id$ */

/* ---------------------------------------------------------------- */

%header %{
EXTERN_C_BEGIN

typedef PetscErrorCode (*matsetvfunc)
  (Mat, PetscInt,const PetscInt[], PetscInt, const PetscInt[],
   const PetscScalar[], InsertMode);

typedef struct PyMatInserterObject {
  PyObject_HEAD
  Mat         mat;
  PetscInt    bs;
  InsertMode  imode;
  PetscTruth  local;
  PetscTruth  blocked;
  matsetvfunc setvalues;
} PyMatInserterObject;

staticforward PyTypeObject* Py_MatInserter_Type;

static int
matsetvals_ass_sub(PyMatInserterObject *mp,
		   PyObject *indices, PyObject *values)
{
  PetscErrorCode ierr;
  PetscTruth valid;
  Mat mat = mp->mat;
  PetscInt bs = mp->bs;
  InsertMode imode = mp->imode;
  
  PyObject *obj_i=NULL, *obj_j=NULL, *obj_v=NULL;
  PyObject *arr_i=NULL, *arr_j=NULL, *arr_v=NULL;

  PetscInt m=0, *im=NULL;
  PetscInt n=0, *in=NULL;
  PetscScalar   *v=NULL;
  
  /* check input objects */
  if (values == NULL) {
    PyErr_SetString(PyExc_TypeError,  
		    "object does not support item deletion");
    return -1;
  }
  if(!PyTuple_Check(indices) || PyTuple_GET_SIZE(indices) != 2) {
    PyErr_SetString(PyExc_IndexError, 
		    "indices must be a tuple with two arrays");
    return -1 ;
  }
  /* check if matrix is valid */
  valid = PETSC_FALSE;
  MatValid(mat, &valid);
  if (!valid) {
    PyErr_SetString(PyExc_RuntimeError, 
		    "matrix object is invalid");
    return -1 ;
  }
  
  obj_i = PyTuple_GET_ITEM(indices, 0);
  obj_j = PyTuple_GET_ITEM(indices, 1);
  obj_v = values;

#define OBJ2ARRAY(obj, type) \
        PyArray_FromAny((obj), PyArray_DescrFromType((type)), \
			0, 0, NPY_CARRAY, NULL)

  arr_i = OBJ2ARRAY(obj_i, PyPetscArray_INT);
  if (arr_i == NULL) goto fail;
  arr_j = OBJ2ARRAY(obj_j, PyPetscArray_INT);
  if (arr_j == NULL) goto fail;
  arr_v = OBJ2ARRAY(obj_v, PyPetscArray_SCALAR);
  if (arr_v == NULL) goto fail;

#undef OBJ2ARRAY
  
  m  = (PetscInt)     PyArray_SIZE(arr_i);
  im = (PetscInt*)    PyArray_DATA(arr_i);
  n  = (PetscInt)     PyArray_SIZE(arr_j);
  in = (PetscInt*)    PyArray_DATA(arr_j);
  v  = (PetscScalar*) PyArray_DATA(arr_v);
  
  if (PyArray_SIZE(arr_v) != m*bs*n*bs) {
    if (mp->blocked)
      PyErr_SetString(PyExc_ValueError,
		      "incompatible matrix block size and "
		      "array sizes in indices and values");
    else
      PyErr_SetString(PyExc_ValueError,
		      "incompatible array sizes in indices and values");
    goto fail;
  }
  
  ierr = (*(mp->setvalues))(mat,m,im,n,in,v,imode);
  if (ierr) { PyErr_SetPetscError(ierr); goto fail; }

  Py_DECREF(arr_i);
  Py_DECREF(arr_j);
  Py_DECREF(arr_v);
  
  return 0;

 fail:
  Py_XDECREF(arr_i);
  Py_XDECREF(arr_j);
  Py_XDECREF(arr_v);
  return -1;
}

static PyMappingMethods matsetvals_as_mapping = {
  (inquiry)0,                        /*mp_length*/
  (binaryfunc)0,                     /*mp_subscript*/
  (objobjargproc)matsetvals_ass_sub, /*mp_ass_subscript*/
};

static int 
matsetvals_get_imode(PyPetscObjectObject *self, PyObject *value,
		     void *closure)
{ 
  return PyInt_FromLong((long)self->imode);
}
static int 
matsetvals_set_imode(PyPetscObjectObject *self, PyObject *value,
		     void *closure)
{ 
  if (value == NULL) { 
    PyErr_SetString(PyExc_TypeError, "cannot delete attribute");
    return -1;
  }
  return 0; 
}

static PyGetSetDef matsetvals_getset[] = {
  {"insert_mode",
   (getter)matsetvals_get_imode, (setter)matsetvals_set_imode,
   "insertion mode", NULL},

  {NULL}  /* Sentinel */
};

static PyTypeObject _Py_MatInserter_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  0,                                    /*ob_size*/
  "MatInserter",                        /*tp_name*/
  sizeof(PyMatInserterObject),          /*tp_basicsize*/
  0,                                    /*tp_itemsize*/
  (destructor)PyObject_Del,             /*tp_dealloc*/
  (printfunc)0,                         /*tp_print*/
  (getattrfunc)0,                       /*tp_getattr*/
  (setattrfunc)0,                       /*tp_setattr*/
  (cmpfunc)0,                           /*tp_compare*/
  (reprfunc)0,                          /*tp_repr*/
  0,                                    /*tp_as_number*/
  0,                                    /*tp_as_sequence*/
  &matsetvals_as_mapping                /*tp_as_mapping*/
};

EXTERN_C_END
%}

%init %{
Py_MatInserter_Type = &_Py_MatInserter_Type;
if (PyType_Ready(Py_MatInserter_Type) < 0)  return;
%}

/* ---------------------------------------------------------------- */

%wrapper %{

#undef  __FUNCT__  
#define __FUNCT__ "MatGetInserter"
static PetscErrorCode 
MatGetInserter(Mat mat, InsertMode imode,
	       PetscTruth local, PetscTruth blocked,
	       PyObject **out)
{
  PetscTruth valid;
  PyMatInserterObject *self;
  
  PetscErrorCode ierr;
  PetscFunctionBegin;
  /* check if mat is valid */
  ierr = MatValid(mat, &valid); CHKERRQ(ierr);
  if (!valid) SETERRQ(PETSC_ERR_ARG_CORRUPT, "invalid matrix");
  /* allocate Python object */
  self = PyObject_NEW(PyMatInserterObject, Py_MatInserter_Type);
  if (self == NULL) SETERRQ(PETSC_ERR_MEM, "allocating a Python object");
  /* initialize Python object */
  self->mat     = mat;
  self->imode   = imode;
  self->local   = local;
  self->blocked = blocked;
  if (blocked) {
    if (local) self->setvalues = MatSetValuesBlockedLocal;
    else       self->setvalues = MatSetValuesBlocked;
    ierr = MatGetBlockSize(mat, &self->bs); 
    if (ierr) PyObject_DEL(self); CHKERRQ(ierr);
  } else {
    if (local) self->setvalues = MatSetValuesLocal;
    else       self->setvalues = MatSetValues;
    self->bs = 1;
  }
  /* result */
  *out = (PyObject *)self;
  PetscFunctionReturn(0);
}

%}

%apply PyObject **OUTPUT { PyObject **out };

static PetscErrorCode 
MatGetInserter(Mat, InsertMode,  PetscTruth, PetscTruth,
	       PyObject **out);

%clear PyObject **out;

/* ---------------------------------------------------------------- */

/*
 * Local Variables:
 * mode: C
 * End:
 */
